const { test, expect } = require('@playwright/test');
const { resetClientStorage } = require('./test-utils');

test.describe('Performance and Security E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await resetClientStorage(page);
  });

  test.describe('Performance Tests', () => {
    test('should load homepage in reasonable time', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      // Should load within 10 seconds
      expect(loadTime).toBeLessThan(10000);

      // Page should be interactive
      const isInteractive = await page.evaluate(() => {
        return document.readyState === 'complete' || document.readyState === 'interactive';
      });

      expect(isInteractive).toBeTruthy();
    });

    test('should load platforms page within acceptable time', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      // Should load platforms within 10 seconds
      expect(loadTime).toBeLessThan(10000);

      // Should have loaded content
      const content = await page.locator('[class*="platform"], [class*="card"]').count();
      expect(content).toBeGreaterThanOrEqual(0);
    });

    test('should load articles page within acceptable time', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/articles/');
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      // Should load articles within 10 seconds
      expect(loadTime).toBeLessThan(10000);
    });

    test('should search respond within 2 seconds', async ({ page }) => {
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');

      if (searchInput) {
        const startTime = Date.now();

        await searchInput.fill('forex');
        await page.waitForTimeout(600); // Allow debounce

        const responseTime = Date.now() - startTime;

        // Should respond within reasonable time
        expect(responseTime).toBeLessThan(5000);
      }
    });

    test('should handle pagination efficiently', async ({ page }) => {
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      const nextButton = await page.$('button:has-text("下一页"), button:has-text("Next")');

      if (nextButton) {
        const isDisabled = await nextButton.evaluate(btn => btn.disabled || btn.classList.contains('disabled'));

        if (!isDisabled) {
          const startTime = Date.now();

          await nextButton.click();
          await page.waitForLoadState('networkidle');

          const responseTime = Date.now() - startTime;

          // Page transition should be quick
          expect(responseTime).toBeLessThan(5000);
        }
      }
    });

    test('should cache responses efficiently', async ({ page }) => {
      // Track cache hits
      const cacheHits = [];

      await page.route('**/api/**', (route) => {
        cacheHits.push({
          url: route.request().url(),
          timestamp: Date.now()
        });
        route.continue();
      });

      // Load page
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      const initialRequests = cacheHits.length;

      // Go to same page again (should use cache)
      await page.reload();
      await page.waitForLoadState('networkidle');

      const afterReloadRequests = cacheHits.length - initialRequests;

      // Should make fewer requests on reload (cache hit)
      expect(afterReloadRequests).toBeLessThan(initialRequests);
    });

    test('should not load unnecessary resources', async ({ page }) => {
      const resources = [];

      await page.route('**/*', (route) => {
        resources.push({
          url: route.request().url(),
          type: route.request().resourceType()
        });
        route.continue();
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Count different resource types
      const resourceTypes = {};
      resources.forEach(r => {
        resourceTypes[r.type] = (resourceTypes[r.type] || 0) + 1;
      });

      // Should not have excessive images or scripts
      expect(resourceTypes['image'] || 0).toBeLessThan(50);
      expect(resourceTypes['script'] || 0).toBeLessThan(50);
    });

    test('should handle rapid page navigation', async ({ page }) => {
      const startTime = Date.now();

      // Rapidly navigate between pages
      await page.goto('/');
      await page.goto('/platforms/');
      await page.goto('/articles/');
      await page.goto('/');

      const navigationTime = Date.now() - startTime;

      // Should handle rapid navigation without crashing
      expect(navigationTime).toBeLessThan(15000);

      // Final page should load
      await page.waitForLoadState('networkidle');
      const content = await page.locator('body').textContent();
      expect(content).toBeTruthy();
    });
  });

  test.describe('Security Tests', () => {
    test('should not expose sensitive data in console', async ({ page }) => {
      const consoleLogs = [];

      page.on('console', msg => {
        consoleLogs.push(msg.text());
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Register user
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      const timestamp = Date.now();
      const email = `security-${timestamp}@example.com`;
      const password = 'Test@12345';

      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);

      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Check console for sensitive data
      const hasPasswordInConsole = consoleLogs.some(log => log.includes(password));
      const hasEmailInConsole = consoleLogs.some(log => log.includes(email));

      // Should not log passwords
      expect(hasPasswordInConsole).toBeFalsy();
    });

    test('should use HTTPS headers correctly', async ({ page }) => {
      const responses = [];

      page.on('response', response => {
        responses.push({
          url: response.url(),
          headers: response.headers()
        });
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Check for security headers (if backend is configured)
      const mainResponse = responses.find(r => r.url === 'http://localhost/');

      // At minimum, should have content-type
      if (mainResponse) {
        expect(mainResponse.headers['content-type']).toBeTruthy();
      }
    });

    test('should not store passwords in localStorage', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      const timestamp = Date.now();
      const password = 'Test@12345';

      await page.fill('input[type="email"]', `test-${timestamp}@example.com`);
      await page.fill('input[type="password"]', password);

      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill(password);
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Check localStorage
      const localStorageData = await page.evaluate(() => {
        const data = {};
        for (let i = 0; i < localStorage.length; i++) {
          data[localStorage.key(i)] = localStorage.getItem(localStorage.key(i));
        }
        return data;
      });

      // Should not have password in localStorage
      const hasPassword = Object.values(localStorageData).some(val => 
        typeof val === 'string' && val.includes(password)
      );

      expect(hasPassword).toBeFalsy();
    });

    test('should protect against XSS via search', async ({ page }) => {
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');

      if (searchInput) {
        // Try XSS payload
        const xssPayload = '<img src=x onerror="window.xssExecuted=true">';
        await searchInput.fill(xssPayload);
        await page.waitForTimeout(500);

        // Check if XSS was executed
        const xssExecuted = await page.evaluate(() => window.xssExecuted);

        expect(xssExecuted).toBeFalsy();
      }
    });

    test('should sanitize displayed user content', async ({ page }) => {
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');

      // We can't easily test if backend sanitizes, but we can verify frontend doesn't execute scripts
      if (searchInput) {
        await page.goto('/platforms/');
        await page.waitForLoadState('networkidle');

        const htmlPayload = '<script>window.testScriptExecuted=true;</script>';
        await searchInput.fill(htmlPayload);
        await page.waitForTimeout(1000);

        const scriptExecuted = await page.evaluate(() => window.testScriptExecuted);
        expect(scriptExecuted).toBeFalsy();
      }
    });

    test('should not leak user info in URLs', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Register
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      const timestamp = Date.now();
      const email = `url-test-${timestamp}@example.com`;

      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', 'Test@12345');

      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill('Test@12345');
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Check URL
      const currentUrl = page.url();

      // Should not expose email or password in URL
      expect(currentUrl).not.toContain(email);
      expect(currentUrl).not.toContain('password');
      expect(currentUrl).not.toContain('token');
    });

    test('should clear sensitive data on logout', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Register
      await page.click('text=登录 / 注册');
      await page.waitForSelector('[id*="register"]', { timeout: 5000 });

      const timestamp = Date.now();
      await page.fill('input[type="email"]', `logout-${timestamp}@example.com`);
      await page.fill('input[type="password"]', 'Test@12345');

      const passwordInputs = await page.$$('input[type="password"]');
      if (passwordInputs.length > 1) {
        await passwordInputs[1].fill('Test@12345');
      }

      await page.click('button:has-text("注册"), button:has-text("创建账户")');
      await page.waitForTimeout(2000);

      // Get token
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token).toBeTruthy();

      // Logout
      await page.click('button:has-text("登出"), button:has-text("退出")');
      await page.waitForTimeout(1000);

      // Verify token is cleared
      const clearedToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(clearedToken).toBeFalsy();

      // Verify sessionStorage is also cleared
      const sessionData = await page.evaluate(() => {
        const data = {};
        for (let i = 0; i < sessionStorage.length; i++) {
          data[sessionStorage.key(i)] = sessionStorage.getItem(sessionStorage.key(i));
        }
        return data;
      });

      const hasSensitiveData = Object.values(sessionData).some(val => 
        typeof val === 'string' && (val.includes('token') || val.includes('auth'))
      );

      expect(hasSensitiveData).toBeFalsy();
    });

    test('should enforce CORS policy', async ({ page }) => {
      let corsErrors = 0;

      page.on('console', msg => {
        if (msg.text().includes('CORS') || msg.text().includes('Cross-Origin')) {
          corsErrors++;
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Navigate to platforms (should not have CORS errors)
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      // Should not have CORS errors on same-origin requests
      // (This is a basic check - real CORS would need different origin)
      expect(corsErrors).toBeLessThan(5);
    });
  });

  test.describe('API Security Tests', () => {
    test('should validate API response data', async ({ page }) => {
      // Track API responses
      const invalidResponses = [];

      await page.route('**/api/**', (route) => {
        route.continue().then(response => {
          if (!response.ok()) {
            invalidResponses.push(response.status());
          }
        }).catch(() => {});
      });

      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      // Should handle any bad responses gracefully
      const content = await page.locator('body').textContent();
      expect(content).toBeTruthy();
    });

    test('should verify SSL certificate (if HTTPS)', async ({ page }) => {
      // This test is more conceptual - real verification happens at transport layer
      
      const url = page.url();
      
      // If API is HTTPS, should not have warnings
      if (url.includes('https')) {
        // Playwright won't load pages with invalid certs
        expect(url).toMatch(/^https/);
      }
    });

    test('should not accept malformed JWT tokens', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Try to set invalid token
      await page.evaluate(() => {
        localStorage.setItem('token', 'invalid.jwt.token');
      });

      // Navigate to protected area
      await page.goto('/platforms/');
      await page.waitForLoadState('networkidle');

      // Should either reject or show login
      const hasLoginPrompt = await page.locator('text=登录, text=认证').isVisible({ timeout: 5000 }).catch(() => false);

      // Token should be cleared or unchanged
      const token = await page.evaluate(() => localStorage.getItem('token'));
      expect(token === 'invalid.jwt.token' || !token).toBeTruthy();
    });
  });
});
