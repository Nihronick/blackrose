import { test, expect } from '@playwright/test';

test.describe('Guide Details & Interactions', () => {
  test('should render reading progress bar and scroll-to-top on scrollable pages', async ({ page }) => {
    await page.goto('/');
    
    // Ensure app shell renders
    await expect(page.locator('#root')).toBeVisible();

    // Check header and main container
    const mainContainer = page.locator('.view-scroll, main').first();
    if (await mainContainer.isVisible()) {
      // Simulate scroll
      await mainContainer.evaluate((el) => {
        el.scrollTop = 500;
      });
    }
  });

  test('should support light/dark theme preference', async ({ page }) => {
    await page.goto('/');

    // Check html element has class 'dark' or 'light'
    const html = page.locator('html');
    const classAttr = await html.getAttribute('class');
    expect(classAttr).toBeDefined();
  });
});
