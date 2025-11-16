async function resetClientStorage(page, prepPath = '/') {
  await page.context().clearCookies();

  if (prepPath) {
    try {
      await page.goto(prepPath);
      await page.waitForLoadState('domcontentloaded');
    } catch (error) {
      // Ignore navigation failures so storage clearing still runs
    }
  }

  try {
    await page.evaluate(() => {
      if (typeof window === 'undefined' || window.location.origin === 'null') {
        return;
      }

      const clearStorage = store => {
        if (typeof store === 'undefined') {
          return;
        }
        store.clear();
      };

      try {
        clearStorage(localStorage);
        clearStorage(sessionStorage);
      } catch (error) {
        if (!(error && error.name === 'SecurityError')) {
          throw error;
        }
      }
    });
  } catch (error) {
    if (!(error && error.name === 'SecurityError')) {
      throw error;
    }
  }
}

module.exports = {
  resetClientStorage,
};
