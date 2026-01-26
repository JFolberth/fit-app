import { test, expect } from '@playwright/test';

// Intercept API calls to avoid needing a backend server
async function mockApi(page) {
  await page.route('**/api/activities', async route => {
    if (route.request().method() === 'POST') {
      return route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'mock-id', type: 'Running', duration: 30, date: '2026-01-21' })
      });
    }
    return route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
  });
}

// Uses baseURL from playwright.config.ts; serve frontend/src via http-server
test('log activity redirects to homepage with success notification', async ({ page }) => {
  await mockApi(page);
  await page.goto('/pages/log-activity.html');
  await page.selectOption('select[name="type"]', 'Running');
  await page.fill('input[name="duration"]', '30');
  await page.fill('input[name="distance"]', '3.1');
  await page.fill('input[name="avgBpm"]', '140');
  await page.click('button[type="submit"]');
  // Should redirect to homepage
  await page.waitForURL('**/index.html');
  // Success notice should appear on homepage
  const notice = page.locator('.notice.success');
  await expect(notice).toHaveText(/Activity saved/i);
});
