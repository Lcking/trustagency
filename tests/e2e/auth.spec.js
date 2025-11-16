const { test, expect } = require('@playwright/test');
const { resetClientStorage } = require('./test-utils');

test.describe('User Authentication E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await resetClientStorage(page);

    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('User Registration', () => {
    test('should successfully register a new user', async ({ page }) => {
      // Click login button to open auth modal
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      // Fill registration form
      const timestamp = Date.now();
      const email = `test-${timestamp}@example.com`;
      const password = 'Test@12345';

      await page.fill('input[placeholder*="邮箱"], input[type="email"]', email);
      await page.fill('input[placeholder*="密码"], input[type="password"]', password);
      
      // Confirm password field
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      // Submit registration form
      await page.click('button:has-text("注册"), button:has-text("创建账户")');

      // Wait for success indication
      await page.waitForTimeout(2000);

      // Verify user is logged in (token in localStorage)
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Verify logout button appears
      await expect(page.locator('button:has-text("登出"), button:has-text("退出")')).toBeVisible({ timeout: 5000 });
    });

    test('should reject registration with invalid email', async ({ page }) => {
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      // Fill form with invalid email
      await page.fill('input[type="email"]', 'invalid-email');
      await page.fill('input[type="password"]', 'Test@12345');

      // Try to submit
      const submitButton = await page.$('button:has-text("注册"), button:has-text("创建账户")');
      if (submitButton) {
        await submitButton.click();
        
        // Should show error or prevent submission
        await page.waitForTimeout(1000);
        const errorMessage = await page.locator('[role="alert"], .error, .alert-danger').isVisible();
        expect(errorMessage).toBeTruthy();
      }
    });

    test('should reject registration with weak password', async ({ page }) => {
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      const timestamp = Date.now();
      const email = `test-${timestamp}@example.com`;

      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', '123'); // Weak password

      // Verify submit button is disabled or shows warning
      const submitButton = await page.$('button:has-text("注册"), button:has-text("创建账户")');
      const isDisabled = await submitButton.evaluate(btn => btn.disabled);
      
      if (isDisabled) {
        expect(isDisabled).toBe(true);
      } else {
        // Try to submit and check for error
        await submitButton.click();
        await page.waitForTimeout(1000);
        const errorMessage = await page.locator('[role="alert"], .error, .alert-danger').isVisible();
        expect(errorMessage).toBeTruthy();
      }
    });

    test('should reject duplicate email registration', async ({ page }) => {
      const email = `duplicate-${Date.now()}@example.com`;
      const password = 'Test@12345';

      // First registration
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.evaluate(() => localStorage.clear());
      await page.reload();

      // Try to register with same email
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs2 = await page.$$('input[type="password"]');
      if (passwordInputs2.length > 1) {
        await passwordInputs2[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(1000);

      // Should show error
      const errorMessage = await page.locator('[role="alert"], .error, .alert-danger').isVisible();
      expect(errorMessage).toBeTruthy();
    });
  });

  test.describe('User Login', () => {
    test('should successfully login with valid credentials', async ({ page }) => {
      // First, create an account
      const email = `login-test-${Date.now()}@example.com`;
      const password = 'Test@12345';

      // Register
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Verify logged in
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.evaluate(() => localStorage.clear());
      await page.reload();

      // Now login with same credentials
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="login"]', { timeout: 5000 });
      
      // Switch to login tab if needed
      const loginTab = await page.$('[id*="login"]');
      if (loginTab) {
        await loginTab.click();
      }

      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);

      // Submit login
      await page.click('button:has-text("登录"), button:has-text("登记")');

      // Wait for login to complete
      await page.waitForTimeout(2000);

      // Verify token is saved
      const newToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(newToken).toBeTruthy();

      // Verify logout button appears
      await expect(page.locator('button:has-text("登出"), button:has-text("退出")')).toBeVisible({ timeout: 5000 });
    });

    test('should reject login with invalid email', async ({ page }) => {
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="login"]', { timeout: 5000 });
      
      const loginTab = await page.$('[id*="login"]');
      if (loginTab) {
        await loginTab.click();
      }

      await page.fill('input[type="email"]', 'nonexistent@example.com');
      await page.fill('input[type="password"]', 'anypassword');

      await page.click('button:has-text("登录"), button:has-text("登记")');
      await page.waitForTimeout(1000);

      // Should show error
      const errorMessage = await page.locator('[role="alert"], .error, .alert-danger').isVisible();
      expect(errorMessage).toBeTruthy();

      // Token should not be saved
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeFalsy();
    });

    test('should reject login with wrong password', async ({ page }) => {
      // Create account first
      const email = `wrong-pass-${Date.now()}@example.com`;
      const correctPassword = 'Test@12345';

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', correctPassword);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(correctPassword);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.evaluate(() => localStorage.clear());
      await page.reload();

      // Try to login with wrong password
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="login"]', { timeout: 5000 });
      
      const loginTab = await page.$('[id*="login"]');
      if (loginTab) {
        await loginTab.click();
      }

      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', 'WrongPassword123');

      await page.click('button:has-text("登录"), button:has-text("登记")');
      await page.waitForTimeout(1000);

      // Should show error
      const errorMessage = await page.locator('[role="alert"], .error, .alert-danger').isVisible();
      expect(errorMessage).toBeTruthy();

      // Token should not be saved
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeFalsy();
    });
  });

  test.describe('User Logout', () => {
    test('should successfully logout and clear session', async ({ page }) => {
      // First register and login
      const email = `logout-test-${Date.now()}@example.com`;
      const password = 'Test@12345';

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Verify logged in
      let token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.waitForTimeout(1000);

      // Verify token is cleared
      token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeFalsy();

      // Verify login button is visible
      await expect(page.locator('text=登录 / 注册')).toBeVisible({ timeout: 5000 });
    });

    test('should prevent access to user-only features after logout', async ({ page }) => {
      // Register and login
      const email = `feature-test-${Date.now()}@example.com`;
      const password = 'Test@12345';

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Try to navigate to platforms page
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      // Verify login prompt is shown or access is denied
      const hasLoginPrompt = await page.locator('text=登录 / 注册, text=请先登录').isVisible({ timeout: 5000 });
      expect(hasLoginPrompt).toBeTruthy();
    });
  });

  test.describe('Token Management', () => {
    test('should maintain session across page navigation', async ({ page }) => {
      // Register and login
      const email = `session-test-${Date.now()}@example.com`;
      const password = 'Test@12345';

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Navigate to different pages
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      // Verify token is still there
      let sessionToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(sessionToken).toBe(token);

      // Navigate to articles
      await page.goto('/articles/');
      await page.waitForLoadState('networkidle');

      // Verify token is still there
      sessionToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(sessionToken).toBe(token);
    });

    test('should clear sensitive data on logout', async ({ page }) => {
      // Register and login
      const email = `secure-test-${Date.now()}@example.com`;
      const password = 'Test@12345';

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      
      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Verify sensitive data exists
      let token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.waitForTimeout(1000);

      // Verify all tokens are cleared
      token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeFalsy();

      // Verify localStorage is mostly empty (or only has non-sensitive data)
      const allData = await page.evaluate(() => {
        const data = {};
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          data[key] = localStorage.getItem(key);
        }
        return data;
      });

      // Should not have token, user, or password related data
      expect(allData.token).toBeUndefined();
      expect(allData.password).toBeUndefined();
    });
  });
});
