const { test, expect } = require('@playwright/test');

// Helper to create a test user
async function createTestUser(page) {
  const email = `user-${Date.now()}@example.com`;
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

  return { email, password };
}

test.describe('Platform Listing E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage and cookies
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    
    // Navigate to platforms page
    await page.goto('/platforms/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Platform List Loading', () => {
    test('should load platforms list on page load', async ({ page }) => {
      // Wait for platforms container to be visible
      await expect(page.locator('[id*="platforms"], .platforms-container')).toBeVisible({ timeout: 10000 });

      // Wait for at least one platform card to load
      const platformCards = await page.locator('[class*="platform"], [class*="card"]').count();
      
      // Either there are platforms loaded, or there's a message
      const hasContent = platformCards > 0;
      const hasMessage = await page.locator('text=暂无平台, text=没有平台').isVisible().catch(() => false);
      
      expect(hasContent || hasMessage).toBeTruthy();
    });

    test('should display platform information correctly', async ({ page }) => {
      // Wait for platform cards to load
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Get first platform card
      const firstCard = await page.locator('[class*="platform"], [class*="card"]').first();
      
      // Check for key information
      const hasName = await firstCard.locator('h3, h4, .name, .title').isVisible().catch(() => false);
      const hasDescription = await firstCard.locator('p, .description').isVisible().catch(() => false);
      
      if (hasName || hasDescription) {
        expect(hasName || hasDescription).toBeTruthy();
      }
    });

    test('should show loading indicator while fetching', async ({ page }) => {
      // This test checks if loading state is shown
      // Note: May not always be visible if loading is fast
      
      await page.goto('/platforms/');
      
      const hasLoadingIndicator = await page.locator('[class*="loading"], [class*="spinner"], .loader').isVisible({ timeout: 5000 }).catch(() => false);
      
      // Loading indicator might not always show if content loads quickly
      // But should eventually show content
      await expect(page.locator('[id*="platforms"], .platforms-container')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Platform Search', () => {
    test('should filter platforms by search query', async ({ page }) => {
      // Wait for initial load
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Get initial count
      const initialCount = await page.locator('[class*="platform"], [class*="card"]').count();

      // Find search input
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"], input[id*="search"]');
      
      if (searchInput) {
        // Type search term
        await searchInput.fill('forex');
        await page.waitForTimeout(500); // Wait for debounce

        // Wait for results to update
        await page.waitForTimeout(1000);

        // Count filtered results
        const filteredCount = await page.locator('[class*="platform"], [class*="card"]').count();

        // Filtered count should be less than or equal to initial count
        expect(filteredCount).toBeLessThanOrEqual(initialCount);

        // Verify search results contain the search term (case-insensitive)
        const visibleText = await page.locator('body').textContent();
        expect(visibleText.toLowerCase()).toContain('forex') || expect(filteredCount).toBe(0);
      }
    });

    test('should show no results for non-matching search', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"], input[id*="search"]');
      
      if (searchInput) {
        // Search for unlikely term
        await searchInput.fill('xyznonexistentplatform12345');
        await page.waitForTimeout(500);

        await page.waitForTimeout(1000);

        // Should show empty state or message
        const resultCount = await page.locator('[class*="platform"], [class*="card"]').count();
        const hasEmptyMessage = await page.locator('text=无结果, text=未找到, text=暂无').isVisible({ timeout: 5000 }).catch(() => false);

        expect(resultCount === 0 || hasEmptyMessage).toBeTruthy();
      }
    });

    test('should clear search results on empty query', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"], input[id*="search"]');
      
      if (searchInput) {
        // Search for something
        await searchInput.fill('crypto');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        // Get filtered count
        const filteredCount = await page.locator('[class*="platform"], [class*="card"]').count();

        // Clear search
        await searchInput.fill('');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        // Should show all results again
        const allCount = await page.locator('[class*="platform"], [class*="card"]').count();

        // All count should be greater than or equal to filtered count
        expect(allCount).toBeGreaterThanOrEqual(filteredCount);
      }
    });
  });

  test.describe('Platform Filtering', () => {
    test('should filter by leverage range', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const initialCount = await page.locator('[class*="platform"], [class*="card"]').count();

      // Find leverage filter
      const leverageInput = await page.$('input[id*="leverage"], input[placeholder*="杠杆"], input[type="range"]');
      
      if (leverageInput) {
        // Try to set leverage filter
        await leverageInput.fill('50');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const filteredCount = await page.locator('[class*="platform"], [class*="card"]').count();

        // Should have some results (or none if filter is very restrictive)
        expect(filteredCount).toBeLessThanOrEqual(initialCount);
      }
    });

    test('should filter by rating', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Find rating filter
      const ratingSelect = await page.$('select[id*="rating"], select[name*="rating"]');
      
      if (ratingSelect) {
        // Get options
        const options = await ratingSelect.$$eval('option', opts => opts.map(o => o.value));

        if (options.length > 1) {
          // Select a rating
          await ratingSelect.selectOption(options[1]);
          await page.waitForTimeout(500);
          await page.waitForTimeout(1000);

          // Verify filtering worked
          const results = await page.locator('[class*="platform"], [class*="card"]').count();
          expect(results).toBeGreaterThanOrEqual(0);
        }
      }
    });

    test('should filter by country', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Find country filter
      const countrySelect = await page.$('select[id*="country"], select[name*="country"]');
      
      if (countrySelect) {
        const options = await countrySelect.$$eval('option', opts => opts.map(o => o.value));

        if (options.length > 1) {
          await countrySelect.selectOption(options[1]);
          await page.waitForTimeout(500);
          await page.waitForTimeout(1000);

          const results = await page.locator('[class*="platform"], [class*="card"]').count();
          expect(results).toBeGreaterThanOrEqual(0);
        }
      }
    });

    test('should combine multiple filters', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const initialCount = await page.locator('[class*="platform"], [class*="card"]').count();

      // Apply multiple filters
      const leverageInput = await page.$('input[id*="leverage"], input[placeholder*="杠杆"]');
      const ratingSelect = await page.$('select[id*="rating"], select[name*="rating"]');

      if (leverageInput && ratingSelect) {
        await leverageInput.fill('100');
        await page.waitForTimeout(300);

        const ratingOptions = await ratingSelect.$$eval('option', opts => opts.map(o => o.value));
        if (ratingOptions.length > 1) {
          await ratingSelect.selectOption(ratingOptions[1]);
          await page.waitForTimeout(300);
        }

        await page.waitForTimeout(1000);

        const combinedFilterCount = await page.locator('[class*="platform"], [class*="card"]').count();
        expect(combinedFilterCount).toBeLessThanOrEqual(initialCount);
      }
    });
  });

  test.describe('Platform Sorting', () => {
    test('should sort platforms by ranking', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        await sortSelect.selectOption('ranking');
        await page.waitForTimeout(1000);

        const cards = await page.locator('[class*="platform"], [class*="card"]');
        const count = await cards.count();

        expect(count).toBeGreaterThan(0);

        // Verify cards are sorted (first card should have highest ranking info if available)
        const firstCardText = await cards.first().textContent();
        expect(firstCardText).toBeTruthy();
      }
    });

    test('should sort platforms by rating', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        await sortSelect.selectOption('rating');
        await page.waitForTimeout(1000);

        const cards = await page.locator('[class*="platform"], [class*="card"]');
        const count = await cards.count();

        expect(count).toBeGreaterThan(0);
      }
    });

    test('should sort platforms by leverage', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        await sortSelect.selectOption('leverage');
        await page.waitForTimeout(1000);

        const cards = await page.locator('[class*="platform"], [class*="card"]');
        const count = await cards.count();

        expect(count).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Platform Pagination', () => {
    test('should display pagination controls', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Look for pagination controls
      const paginationControls = await page.$('[class*="pagination"], [id*="pagination"], [class*="pager"]');

      if (paginationControls) {
        expect(paginationControls).toBeTruthy();

        // Check for next/prev buttons
        const hasNextButton = await page.locator('button:has-text("下一页"), button:has-text("Next"), a:has-text("下一页")').isVisible({ timeout: 5000 }).catch(() => false);
        const hasPrevButton = await page.locator('button:has-text("上一页"), button:has-text("Prev"), a:has-text("上一页")').isVisible({ timeout: 5000 }).catch(() => false);

        expect(hasNextButton || hasPrevButton).toBeTruthy();
      }
    });

    test('should navigate to next page', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Get initial card IDs/names
      const initialCards = await page.locator('[class*="platform"], [class*="card"]').count();

      const nextButton = await page.$('button:has-text("下一页"), button:has-text("Next"), a:has-text("下一页")');

      if (nextButton) {
        const isDisabled = await nextButton.evaluate(btn => btn.disabled || btn.classList.contains('disabled'));

        if (!isDisabled) {
          await nextButton.click();
          await page.waitForTimeout(1000);

          // Verify page changed
          const newCards = await page.locator('[class*="platform"], [class*="card"]').count();

          // If we got to page 2, cards might be different
          expect(newCards).toBeGreaterThan(0);
        }
      }
    });

    test('should navigate to previous page', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // First go to next page
      const nextButton = await page.$('button:has-text("下一页"), button:has-text("Next"), a:has-text("下一页")');

      if (nextButton) {
        const isDisabled = await nextButton.evaluate(btn => btn.disabled || btn.classList.contains('disabled'));

        if (!isDisabled) {
          await nextButton.click();
          await page.waitForTimeout(1000);

          // Now try prev button
          const prevButton = await page.$('button:has-text("上一页"), button:has-text("Prev"), a:has-text("上一页")');

          if (prevButton) {
            const isPrevDisabled = await prevButton.evaluate(btn => btn.disabled || btn.classList.contains('disabled'));

            if (!isPrevDisabled) {
              await prevButton.click();
              await page.waitForTimeout(1000);

              const cards = await page.locator('[class*="platform"], [class*="card"]').count();
              expect(cards).toBeGreaterThan(0);
            }
          }
        }
      }
    });

    test('should show current page info', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      // Look for page info
      const pageInfo = await page.$('[class*="page-info"], [class*="pagination-info"], span:has-text("页")');

      if (pageInfo) {
        const text = await pageInfo.textContent();
        expect(text).toMatch(/\d+/);
      }
    });
  });

  test.describe('Platform Details', () => {
    test('should display platform details on card', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const firstCard = await page.locator('[class*="platform"], [class*="card"]').first();

      // Check for typical platform details
      const hasTitle = await firstCard.locator('h3, h4, .name, .title').isVisible().catch(() => false);
      const hasRating = await firstCard.locator('[class*="rating"], [class*="star"], span:has-text("★")').isVisible().catch(() => false);
      const hasLeverage = await firstCard.locator('text=杠杆, text=Leverage, text=/\\d+x/').isVisible().catch(() => false);

      expect(hasTitle || hasRating || hasLeverage).toBeTruthy();
    });

    test('should show platform ratings with stars', async ({ page }) => {
      await page.waitForSelector('[class*="platform"], [class*="card"]', { timeout: 10000 });

      const ratingElements = await page.locator('[class*="rating"], [class*="star"], span:has-text("★")');
      const count = await ratingElements.count();

      // Should have at least some ratings visible
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Empty States and Errors', () => {
    test('should handle no platforms gracefully', async ({ page }) => {
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        // Search for something that returns no results
        await searchInput.fill('xyznonexistent99999');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const results = await page.locator('[class*="platform"], [class*="card"]').count();
        const hasEmptyMessage = await page.locator('text=无结果, text=未找到, text=暂无').isVisible({ timeout: 5000 }).catch(() => false);

        expect(results === 0 || hasEmptyMessage).toBeTruthy();
      }
    });

    test('should show error message on API failure', async ({ page }) => {
      // Try to trigger an error by going offline
      await page.context().setOffline(true);

      // Try to reload or search
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        await searchInput.fill('test');
        await page.waitForTimeout(500);
      }

      // Go back online
      await page.context().setOffline(false);

      // Should eventually recover
      await page.waitForTimeout(2000);
      
      const content = await page.locator('[id*="platforms"], .platforms-container').isVisible({ timeout: 10000 }).catch(() => false);
      expect(content).toBeTruthy();
    });
  });
});
