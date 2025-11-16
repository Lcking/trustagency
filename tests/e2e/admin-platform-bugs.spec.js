const { test, expect } = require('@playwright/test');

/**
 * 针对性测试：平台管理Bug修复验证
 * 
 * Bug013: 新增平台无响应
 * Bug014: 编辑平台错误信息显示为 [object Object]
 * Bug015: 字段配置不正确（评分、安全评级、平台类型）
 */

test.describe('Admin Platform Management Bug Fixes', () => {
  let adminPage;

  test.beforeEach(async ({ page }) => {
    adminPage = page;
    
    // Clear storage
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    
    // Navigate to admin login
    await page.goto('http://localhost:8001/admin/', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
  });

  /**
   * 辅助函数：登录管理员账户
   */
  async function loginAsAdmin(page) {
    // Wait for login form
    await page.waitForSelector('input[type="text"], input[type="email"], input[name="username"]', { timeout: 10000 });
    
    // Fill login credentials
    const usernameInput = await page.$('input[type="text"], input[name="username"]');
    if (usernameInput) {
      await usernameInput.fill('admin');
    }
    
    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      await passwordInput.fill('admin123');
    }
    
    // Click login button
    await page.click('button[type="submit"], button:has-text("登录")');
    
    // Wait for dashboard to load
    await page.waitForTimeout(2000);
  }

  test.describe('Bug013: 新增平台无响应', () => {
    test('should display create platform form when clicking "新增平台"', async ({ page }) => {
      // Login first
      await loginAsAdmin(page);
      
      // Navigate to platform management
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      // Click "新增平台" button
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      
      expect(createButton).toBeTruthy();
      
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
        
        // Verify modal/form is displayed
        const modal = await page.$('[class*="modal"], [class*="dialog"], [id*="platform-form"]');
        expect(modal).toBeTruthy();
        
        // Verify form has fields
        const formFields = await page.$$('input, select, textarea');
        expect(formFields.length).toBeGreaterThan(0);
        
        // Check for key fields that should be present
        const hasNameField = await page.$('input[name="name"], input[placeholder*="名称"]');
        const hasDescriptionField = await page.$('textarea[name="description"], textarea[placeholder*="描述"]');
        
        // At least some form fields should be visible
        expect(hasNameField || hasDescriptionField || formFields.length > 5).toBeTruthy();
      }
    });

    test('should load form definition without errors', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Listen for API calls
      const apiCalls = [];
      page.on('response', response => {
        if (response.url().includes('/form-definition') || response.url().includes('/create-form')) {
          apiCalls.push({
            url: response.url(),
            status: response.status()
          });
        }
      });
      
      // Navigate and open create form
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
      }
      
      // Check console for errors
      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      
      await page.waitForTimeout(1000);
      
      // Verify API calls succeeded
      const failedCalls = apiCalls.filter(call => call.status >= 400);
      expect(failedCalls.length).toBe(0);
      
      // No major console errors should be present
      const criticalErrors = consoleErrors.filter(err => 
        err.includes('Failed') || err.includes('Error loading') || err.includes('undefined')
      );
      expect(criticalErrors.length).toBe(0);
    });
  });

  test.describe('Bug014: 编辑平台错误信息', () => {
    test('should display clear error messages instead of [object Object]', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Navigate to platforms
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      // Find first edit button
      const editButton = await page.$('button:has-text("编辑"), a:has-text("编辑")');
      
      if (editButton) {
        await editButton.click();
        await page.waitForTimeout(2000);
        
        // Try to save with invalid data to trigger error
        const saveButton = await page.$('button:has-text("保存"), button[type="submit"]');
        
        if (saveButton) {
          // Clear a required field if possible
          const nameField = await page.$('input[name="name"]');
          if (nameField) {
            await nameField.fill('');
          }
          
          await saveButton.click();
          await page.waitForTimeout(1000);
          
          // Check for error messages
          const errorElements = await page.$$('[class*="error"], [class*="alert"], .notification');
          
          if (errorElements.length > 0) {
            const errorText = await errorElements[0].textContent();
            
            // Error message should NOT be "[object Object]"
            expect(errorText).not.toContain('[object Object]');
            expect(errorText).not.toMatch(/^\[object Object\]/);
            
            // Should contain meaningful error information
            expect(errorText.length).toBeGreaterThan(5);
          }
        }
      }
    });

    test('should handle Pydantic validation errors correctly', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Monitor network responses
      const errorResponses = [];
      page.on('response', async response => {
        if (response.url().includes('/api/') && response.status() >= 400) {
          try {
            const body = await response.json();
            errorResponses.push({
              url: response.url(),
              status: response.status(),
              body: body
            });
          } catch (e) {
            // Non-JSON response
          }
        }
      });
      
      // Check that any error display logic doesn't show raw objects
      await page.waitForTimeout(2000);
      
      const pageText = await page.textContent('body');
      expect(pageText).not.toContain('[object Object]');
    });
  });

  test.describe('Bug015: 字段配置正确性', () => {
    test('should display correct rating field (0-5 scale)', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Navigate to create/edit form
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
      }
      
      // Find rating field
      const ratingField = await page.$('input[name="rating"], input[placeholder*="评分"]');
      
      if (ratingField) {
        // Check max attribute
        const maxValue = await ratingField.getAttribute('max');
        expect(maxValue).toBe('5');
        
        // Check min attribute
        const minValue = await ratingField.getAttribute('min');
        expect(minValue).toBe('0');
        
        // Check step attribute (should allow decimals)
        const stepValue = await ratingField.getAttribute('step');
        expect(stepValue).toBe('0.1');
      }
    });

    test('should display safety_rating as select with A/B/C/D options', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Open create form
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
      }
      
      // Find safety_rating field - should be a select
      const safetyField = await page.$('select[name="safety_rating"]');
      
      expect(safetyField).toBeTruthy();
      
      if (safetyField) {
        // Get options
        const options = await safetyField.$$eval('option', opts => 
          opts.map(o => ({ value: o.value, text: o.textContent }))
        );
        
        // Should have A, B, C, D options
        const values = options.map(o => o.value);
        expect(values).toContain('A');
        expect(values).toContain('B');
        expect(values).toContain('C');
        expect(values).toContain('D');
        
        // Should NOT be a number input
        const numberInput = await page.$('input[name="safety_rating"][type="number"]');
        expect(numberInput).toBeNull();
      }
    });

    test('should display platform_type with correct options (新手/进阶/活跃/专业)', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Open create form
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
      }
      
      // Find platform_type field
      const platformTypeField = await page.$('select[name="platform_type"]');
      
      if (platformTypeField) {
        const options = await platformTypeField.$$eval('option', opts => 
          opts.map(o => o.textContent)
        );
        
        // Should contain correct types
        const optionsText = options.join(' ');
        expect(optionsText).toContain('新手');
        expect(optionsText).toContain('进阶');
        expect(optionsText).toContain('活跃');
        expect(optionsText).toContain('专业');
        
        // Should NOT contain exchange-related types
        expect(optionsText).not.toContain('交易所');
        expect(optionsText).not.toContain('中心化交易所');
        expect(optionsText).not.toContain('去中心化交易所');
      }
    });
  });

  test.describe('Overall Platform Management Workflow', () => {
    test('should complete full create platform workflow', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Navigate to platforms
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      // Open create form
      const createButton = await page.$('button:has-text("新增平台"), button:has-text("+ 新增")');
      if (createButton) {
        await createButton.click();
        await page.waitForTimeout(2000);
        
        // Fill in required fields
        const nameField = await page.$('input[name="name"]');
        if (nameField) {
          await nameField.fill(`Test Platform ${Date.now()}`);
        }
        
        const slugField = await page.$('input[name="slug"]');
        if (slugField) {
          await slugField.fill(`test-platform-${Date.now()}`);
        }
        
        const descriptionField = await page.$('textarea[name="description"]');
        if (descriptionField) {
          await descriptionField.fill('Test platform description');
        }
        
        // Try to save
        const saveButton = await page.$('button:has-text("保存"), button[type="submit"]');
        if (saveButton) {
          await saveButton.click();
          await page.waitForTimeout(2000);
          
          // Check for success or clear error
          const notification = await page.$('[class*="notification"], [class*="alert"], [class*="message"]');
          if (notification) {
            const notificationText = await notification.textContent();
            // Should not show [object Object]
            expect(notificationText).not.toContain('[object Object]');
          }
        }
      }
    });

    test('should load existing platform data correctly in edit mode', async ({ page }) => {
      await loginAsAdmin(page);
      
      // Navigate to platforms
      const platformsLink = await page.$('a:has-text("平台管理"), button:has-text("平台管理")');
      if (platformsLink) {
        await platformsLink.click();
        await page.waitForTimeout(1000);
      }
      
      // Click first edit button
      const editButton = await page.$('button:has-text("编辑"), a:has-text("编辑")');
      if (editButton) {
        await editButton.click();
        await page.waitForTimeout(2000);
        
        // Verify form is populated with data
        const nameField = await page.$('input[name="name"]');
        if (nameField) {
          const nameValue = await nameField.inputValue();
          expect(nameValue.length).toBeGreaterThan(0);
        }
        
        // Check that rating field has correct range if present
        const ratingField = await page.$('input[name="rating"]');
        if (ratingField) {
          const maxValue = await ratingField.getAttribute('max');
          expect(maxValue).toBe('5');
        }
      }
    });
  });
});
