import { test, expect } from '@playwright/test';

async function mockApi(page) {
  await page.route('**/api/activities**', async route => {
    const url = route.request().url();
    if (url.includes('type=Running')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: '1', type: 'Running', duration: 30, distance: 3.1, avgBpm: 140, date: '2026-01-20', createdAt: '2026-01-20T12:00:00Z', updatedAt: '2026-01-20T12:00:00Z' },
        ])
      });
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: '1', type: 'Running', duration: 30, distance: 3.1, avgBpm: 140, date: '2026-01-20', createdAt: '2026-01-20T12:00:00Z', updatedAt: '2026-01-20T12:00:00Z' },
        { id: '2', type: 'Rowing', duration: 25, distance: null, avgBpm: 130, date: '2026-01-21', createdAt: '2026-01-21T12:00:00Z', updatedAt: '2026-01-21T12:00:00Z' },
      ])
    });
  });
}

test('history page loads and filters by type', async ({ page }) => {
  await mockApi(page);
  await page.goto('/pages/history.html');
  // Wait for activities to load
  await expect(page.locator('ul.activity-list li')).toHaveCount(2);
  // Filter to Running by clicking the Running button
  await page.click('button.filter-btn:has-text("Running")');
  await expect(page.locator('ul.activity-list li')).toHaveCount(1);
  await expect(page.locator('ul.activity-list li').first()).toContainText('Running');
});
