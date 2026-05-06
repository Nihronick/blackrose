import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');
  // Ожидаем, что на главной странице есть какой-то базовый текст или заголовок
  // В BlackRose это может быть "BlackRose" или элементы дашборда
  await expect(page).toHaveTitle(/BlackRose/i);
});

test('api health check via frontend proxy', async ({ page }) => {
  const response = await page.request.get('http://localhost:8000/api/health');
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.status).toBe('ok');
});
