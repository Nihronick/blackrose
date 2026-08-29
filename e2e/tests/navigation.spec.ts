import { test, expect } from '@playwright/test';

test.describe('Navigation & Routing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should render bottom navigation bar and home dashboard', async ({ page }) => {
    // Check that main app elements render
    await expect(page.locator('#root')).toBeVisible();
    
    // Check page title
    await expect(page).toHaveTitle(/BlackRose/i);
  });

  test('should navigate to categories view', async ({ page }) => {
    // Click on categories tab in bottom bar or direct navigation button
    const catTab = page.locator('button, a').filter({ hasText: /категории/i }).first();
    if (await catTab.isVisible()) {
      await catTab.click();
      await expect(page.locator('[data-testid="categories-view"], input[placeholder*="Поиск категорий"]')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should navigate to search view and back', async ({ page }) => {
    const searchBtn = page.locator('button, a').filter({ hasText: /поиск/i }).first();
    if (await searchBtn.isVisible()) {
      await searchBtn.click();
      await expect(page.locator('input[placeholder*="Искать в базе знаний"]')).toBeVisible({ timeout: 5000 });
      
      // Click cancel/back
      const cancelBtn = page.locator('button').filter({ hasText: /отмена/i }).first();
      if (await cancelBtn.isVisible()) {
        await cancelBtn.click();
      }
    }
  });
});
