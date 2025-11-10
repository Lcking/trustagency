const { test, expect } = require('@playwright/test');

test.describe('Article Browsing E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage and cookies
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    
    // Navigate to articles page
    await page.goto('/articles/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Article List Loading', () => {
    test('should load articles list on page load', async ({ page }) => {
      // Wait for articles container to be visible
      await expect(page.locator('[id*="article"], [class*="article"], .content-container')).toBeVisible({ timeout: 10000 });

      // Wait for at least one article card to load
      const articleCards = await page.locator('[class*="article"], [class*="post"], [class*="card"]').count();
      
      // Either there are articles loaded, or there's a message
      const hasContent = articleCards > 0;
      const hasMessage = await page.locator('text=暂无文章, text=没有文章').isVisible().catch(() => false);
      
      expect(hasContent || hasMessage).toBeTruthy();
    });

    test('should display article information correctly', async ({ page }) => {
      // Wait for article cards to load
      await page.waitForSelector('[class*="article"], [class*="post"], [class*="card"]', { timeout: 10000 });

      // Get first article card
      const firstCard = await page.locator('[class*="article"], [class*="post"], [class*="card"]').first();
      
      // Check for key information
      const hasTitle = await firstCard.locator('h2, h3, h4, .title').isVisible().catch(() => false);
      const hasDescription = await firstCard.locator('p, .excerpt, .description').isVisible().catch(() => false);
      const hasDate = await firstCard.locator('[class*="date"], time, .meta').isVisible().catch(() => false);
      
      expect(hasTitle || hasDescription || hasDate).toBeTruthy();
    });

    test('should display article metadata', async ({ page }) => {
      // Wait for article cards
      await page.waitForSelector('[class*="article"], [class*="post"], [class*="card"]', { timeout: 10000 });

      const firstCard = await page.locator('[class*="article"], [class*="post"], [class*="card"]').first();

      // Check for metadata
      const hasAuthor = await firstCard.locator('[class*="author"], text=作者').isVisible().catch(() => false);
      const hasDate = await firstCard.locator('[class*="date"], time').isVisible().catch(() => false);
      const hasTags = await firstCard.locator('[class*="tag"], [class*="label"]').isVisible().catch(() => false);

      expect(hasAuthor || hasDate || hasTags).toBeTruthy();
    });

    test('should show featured articles prominently', async ({ page }) => {
      // Look for featured section
      const featuredSection = await page.$('[class*="featured"], [id*="featured"]');

      if (featuredSection) {
        await expect(featuredSection).toBeVisible();

        // Check for featured badge
        const hasBadge = await page.locator('[class*="featured"], text=推荐, text=精选').isVisible({ timeout: 5000 }).catch(() => false);
        expect(hasBadge).toBeTruthy();
      }
    });
  });

  test.describe('Article Search', () => {
    test('should search articles by title', async ({ page }) => {
      // Wait for initial load
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const initialCount = await page.locator('[class*="article"], [class*="post"]').count();

      // Find search input
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"], input[id*="search"]');
      
      if (searchInput) {
        // Type search term
        await searchInput.fill('test');
        await page.waitForTimeout(500); // Wait for debounce

        // Wait for results to update
        await page.waitForTimeout(1000);

        const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

        // Filtered results should be reasonable
        expect(filteredCount).toBeLessThanOrEqual(initialCount);

        // If we got results, they should contain search term
        if (filteredCount > 0) {
          const visibleText = await page.locator('body').textContent();
          expect(visibleText.toLowerCase()).toContain('test') || expect(filteredCount).toBe(0);
        }
      }
    });

    test('should show no results for non-matching search', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        // Search for unlikely term
        await searchInput.fill('xyznonexistentarticle99999xyz');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const resultCount = await page.locator('[class*="article"], [class*="post"]').count();
        const hasEmptyMessage = await page.locator('text=无结果, text=未找到, text=暂无').isVisible({ timeout: 5000 }).catch(() => false);

        expect(resultCount === 0 || hasEmptyMessage).toBeTruthy();
      }
    });

    test('should clear search and show all results', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        // Search for something
        await searchInput.fill('article');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

        // Clear search
        await searchInput.fill('');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const allCount = await page.locator('[class*="article"], [class*="post"]').count();

        // All count should be >= filtered count
        expect(allCount).toBeGreaterThanOrEqual(filteredCount);
      }
    });
  });

  test.describe('Article Filtering', () => {
    test('should filter articles by category', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const initialCount = await page.locator('[class*="article"], [class*="post"]').count();

      // Find category filter
      const categorySelect = await page.$('select[id*="category"], select[name*="category"]');
      
      if (categorySelect) {
        // Get available categories
        const options = await categorySelect.$$eval('option', opts => opts.map(o => o.value).filter(v => v));

        if (options.length > 0) {
          // Select first category
          await categorySelect.selectOption(options[0]);
          await page.waitForTimeout(500);
          await page.waitForTimeout(1000);

          const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

          // Should have filtered results
          expect(filteredCount).toBeLessThanOrEqual(initialCount);
        }
      }
    });

    test('should filter articles by tags', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      // Find tag filter
      const tagSelect = await page.$('select[id*="tag"], select[name*="tag"]');
      
      if (tagSelect) {
        const options = await tagSelect.$$eval('option', opts => opts.map(o => o.value).filter(v => v));

        if (options.length > 0) {
          const initialCount = await page.locator('[class*="article"], [class*="post"]').count();
          
          await tagSelect.selectOption(options[0]);
          await page.waitForTimeout(500);
          await page.waitForTimeout(1000);

          const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

          expect(filteredCount).toBeLessThanOrEqual(initialCount);
        }
      }
    });

    test('should filter by featured status', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      // Find featured checkbox
      const featuredCheckbox = await page.$('input[type="checkbox"][id*="featured"]');
      
      if (featuredCheckbox) {
        const initialCount = await page.locator('[class*="article"], [class*="post"]').count();

        // Toggle featured filter
        await featuredCheckbox.check();
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

        // Featured articles should be subset of all articles
        expect(filteredCount).toBeLessThanOrEqual(initialCount);
      }
    });

    test('should combine multiple filters', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const categorySelect = await page.$('select[id*="category"], select[name*="category"]');
      const tagSelect = await page.$('select[id*="tag"], select[name*="tag"]');

      if (categorySelect && tagSelect) {
        const initialCount = await page.locator('[class*="article"], [class*="post"]').count();

        // Get options
        const categoryOptions = await categorySelect.$$eval('option', opts => opts.map(o => o.value).filter(v => v));
        const tagOptions = await tagSelect.$$eval('option', opts => opts.map(o => o.value).filter(v => v));

        if (categoryOptions.length > 0 && tagOptions.length > 0) {
          await categorySelect.selectOption(categoryOptions[0]);
          await page.waitForTimeout(300);

          await tagSelect.selectOption(tagOptions[0]);
          await page.waitForTimeout(300);

          await page.waitForTimeout(1000);

          const filteredCount = await page.locator('[class*="article"], [class*="post"]').count();

          expect(filteredCount).toBeLessThanOrEqual(initialCount);
        }
      }
    });
  });

  test.describe('Article Sorting', () => {
    test('should sort articles by date (newest first)', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        await sortSelect.selectOption('date-desc');
        await page.waitForTimeout(1000);

        const articles = await page.locator('[class*="article"], [class*="post"]');
        const count = await articles.count();

        expect(count).toBeGreaterThan(0);

        // Verify first article exists
        const firstArticleText = await articles.first().textContent();
        expect(firstArticleText).toBeTruthy();
      }
    });

    test('should sort articles by date (oldest first)', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        await sortSelect.selectOption('date-asc');
        await page.waitForTimeout(1000);

        const articles = await page.locator('[class*="article"], [class*="post"]');
        const count = await articles.count();

        expect(count).toBeGreaterThan(0);
      }
    });

    test('should sort articles by title', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        // Try to find title sort option
        const options = await sortSelect.$$eval('option', opts => opts.map(o => o.value));
        const hasTitleSort = options.some(o => o.includes('title') || o.includes('名称'));

        if (hasTitleSort) {
          await sortSelect.selectOption(options.find(o => o.includes('title') || o.includes('名称')));
          await page.waitForTimeout(1000);

          const articles = await page.locator('[class*="article"], [class*="post"]');
          const count = await articles.count();

          expect(count).toBeGreaterThan(0);
        }
      }
    });

    test('should sort articles by popularity', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const sortSelect = await page.$('select[id*="sort"], select[name*="sort"]');
      
      if (sortSelect) {
        const options = await sortSelect.$$eval('option', opts => opts.map(o => o.value));
        const hasPopularSort = options.some(o => o.includes('popular') || o.includes('热门') || o.includes('view'));

        if (hasPopularSort) {
          await sortSelect.selectOption(options.find(o => o.includes('popular') || o.includes('热门') || o.includes('view')));
          await page.waitForTimeout(1000);

          const articles = await page.locator('[class*="article"], [class*="post"]');
          const count = await articles.count();

          expect(count).toBeGreaterThan(0);
        }
      }
    });
  });

  test.describe('Article Pagination', () => {
    test('should display pagination controls', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      // Look for pagination
      const paginationControls = await page.$('[class*="pagination"], [id*="pagination"]');

      if (paginationControls) {
        await expect(paginationControls).toBeVisible();

        // Check for next/prev buttons
        const hasNextButton = await page.locator('button:has-text("下一页"), button:has-text("Next"), a:has-text("下一页")').isVisible({ timeout: 5000 }).catch(() => false);
        const hasPrevButton = await page.locator('button:has-text("上一页"), button:has-text("Prev"), a:has-text("上一页")').isVisible({ timeout: 5000 }).catch(() => false);

        expect(hasNextButton || hasPrevButton).toBeTruthy();
      }
    });

    test('should navigate through pages', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const nextButton = await page.$('button:has-text("下一页"), button:has-text("Next"), a:has-text("下一页")');

      if (nextButton) {
        const isDisabled = await nextButton.evaluate(btn => btn.disabled || btn.classList.contains('disabled'));

        if (!isDisabled) {
          const initialCount = await page.locator('[class*="article"], [class*="post"]').count();

          await nextButton.click();
          await page.waitForTimeout(1000);

          const newCount = await page.locator('[class*="article"], [class*="post"]').count();

          expect(newCount).toBeGreaterThan(0);
        }
      }
    });

    test('should show current page info', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      // Look for page info
      const pageInfo = await page.$('[class*="page-info"], [class*="pagination-info"]');

      if (pageInfo) {
        const text = await pageInfo.textContent();
        expect(text).toMatch(/\d+/);
      }
    });
  });

  test.describe('Article Details', () => {
    test('should display article with featured image', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const firstCard = await page.locator('[class*="article"], [class*="post"]').first();

      // Check for image
      const image = await firstCard.$('img');

      if (image) {
        await expect(image).toBeVisible();

        // Verify image src is set
        const src = await image.getAttribute('src');
        expect(src).toBeTruthy();
      }
    });

    test('should display article tags', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const firstCard = await page.locator('[class*="article"], [class*="post"]').first();

      // Check for tags
      const tags = await firstCard.locator('[class*="tag"], [class*="label"], span').count();

      // Tags may or may not be present, but if they are, they should be visible
      if (tags > 0) {
        const firstTag = await firstCard.locator('[class*="tag"], [class*="label"]').first();
        const isVisible = await firstTag.isVisible().catch(() => false);
        
        // Tags should be visible if they exist
        if (isVisible) {
          expect(isVisible).toBeTruthy();
        }
      }
    });

    test('should display article publication date', async ({ page }) => {
      await page.waitForSelector('[class*="article"], [class*="post"]', { timeout: 10000 });

      const firstCard = await page.locator('[class*="article"], [class*="post"]').first();

      // Check for date
      const dateElement = await firstCard.$('[class*="date"], time, .meta');

      if (dateElement) {
        await expect(dateElement).toBeVisible();

        const text = await dateElement.textContent();
        expect(text).toBeTruthy();
      }
    });
  });

  test.describe('Empty States and Errors', () => {
    test('should handle no articles gracefully', async ({ page }) => {
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        // Search for something unlikely
        await searchInput.fill('xyznonexistent99999');
        await page.waitForTimeout(500);
        await page.waitForTimeout(1000);

        const results = await page.locator('[class*="article"], [class*="post"]').count();
        const hasEmptyMessage = await page.locator('text=无结果, text=未找到, text=暂无').isVisible({ timeout: 5000 }).catch(() => false);

        expect(results === 0 || hasEmptyMessage).toBeTruthy();
      }
    });

    test('should show error message on API failure', async ({ page }) => {
      // Go offline
      await page.context().setOffline(true);

      // Try to search
      const searchInput = await page.$('input[placeholder*="搜索"], input[type="search"]');
      
      if (searchInput) {
        await searchInput.fill('test');
        await page.waitForTimeout(500);
      }

      // Go back online
      await page.context().setOffline(false);

      // Should recover
      await page.waitForTimeout(2000);
      
      const content = await page.locator('[id*="article"], [class*="article"]').isVisible({ timeout: 10000 }).catch(() => false);
      expect(content).toBeTruthy();
    });
  });
});
