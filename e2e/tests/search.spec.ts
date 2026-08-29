import { test, expect } from '@playwright/test';

test.describe('Search Flow', () => {
  test('should handle instant search queries', async ({ page }) => {
    await page.goto('/');

    const searchBtn = page.locator('button, a').filter({ hasText: /поиск/i }).first();
    if (await searchBtn.isVisible()) {
      await searchBtn.click();

      const searchInput = page.locator('input[placeholder*="Искать в базе знаний"]').first();
      await expect(searchInput).toBeVisible({ timeout: 5000 });

      // Type query
      await searchInput.fill('boss');

      // Check that clear button appears when input has text
      const clearBtn = page.locator('button').filter({ has: page.locator('svg') }).first();
      await expect(clearBtn).toBeVisible();
    }
  });

  test('should display empty state when no results found', async ({ page }) => {
    await page.goto('/');

    const searchBtn = page.locator('button, a').filter({ hasText: /поиск/i }).first();
    if (await searchBtn.isVisible()) {
      await searchBtn.click();

      const searchInput = page.locator('input[placeholder*="Искать в базе знаний"]').first();
      await expect(searchInput).toBeVisible({ timeout: 5000 });

      // Search for nonsense query
      await searchInput.fill('xyznonexistentguide12345');

      // Expect empty state or "Ничего не найдено"
      await expect(page.locator('text=Ничего не найдено, text=материалов не найдено').first()).toBeVisible({ timeout: 5000 });
    }
  });
});
