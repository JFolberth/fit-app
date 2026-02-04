import { test, expect, Page, Route } from '@playwright/test';

async function mockApi(page: Page) {
  await page.route('**/api/activities**', async (route: Route) => {
    const url = route.request().url();
    const method = route.request().method();
    
    // Handle PUT request for edit
    if (method === 'PUT') {
      const body = route.request().postDataJSON();
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          ...body,
          createdAt: '2026-01-20T12:00:00Z',
          updatedAt: '2026-02-03T12:00:00Z'
        })
      });
    }
    
    // Handle DELETE request
    if (method === 'DELETE') {
      return route.fulfill({
        status: 204,
        body: ''
      });
    }
    
    // Handle GET requests
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

async function mockApiWithEditValidationError(page: Page) {
  await page.route('**/api/activities**', async (route: Route) => {
    const method = route.request().method();
    
    // Handle PUT request with validation error
    if (method === 'PUT') {
      return route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Input should be greater than or equal to 20' })
      });
    }
    
    // Handle GET requests
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: '1', type: 'Running', duration: 30, distance: 3.1, avgBpm: 140, date: '2026-01-20', createdAt: '2026-01-20T12:00:00Z', updatedAt: '2026-01-20T12:00:00Z' },
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

// Edit Activity Tests
test.describe('Edit Activity', () => {
  test('edit button opens modal with pre-populated data', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    // Wait for activities to load
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Click edit button on first activity
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    
    // Verify modal is visible
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Verify form is pre-populated with activity data
    await expect(page.locator('#edit-type')).toHaveValue('Running');
    await expect(page.locator('#edit-duration')).toHaveValue('30');
    await expect(page.locator('#edit-distance')).toHaveValue('3.1');
    await expect(page.locator('#edit-avgBpm')).toHaveValue('140');
    await expect(page.locator('#edit-date')).toHaveValue('2026-01-20');
  });

  test('edit modal can be cancelled', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open edit modal
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Click cancel button
    await page.click('#edit-cancel');
    
    // Modal should be hidden
    await expect(page.locator('#edit-modal')).toBeHidden();
  });

  test('edit modal closes on X button click', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open edit modal
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Click close button
    await page.click('#edit-modal-close');
    
    // Modal should be hidden
    await expect(page.locator('#edit-modal')).toBeHidden();
  });

  test('edit modal closes on Escape key', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open edit modal
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Press Escape
    await page.keyboard.press('Escape');
    
    // Modal should be hidden
    await expect(page.locator('#edit-modal')).toBeHidden();
  });

  test('successful edit shows success notification', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open edit modal
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Modify duration
    await page.fill('#edit-duration', '45');
    
    // Submit form
    await page.click('#edit-save');
    
    // Modal should close and success notification should appear
    await expect(page.locator('#edit-modal')).toBeHidden();
    await expect(page.locator('.notice.success')).toContainText('Activity updated successfully');
  });

  test('edit validation error displays in modal', async ({ page }) => {
    await mockApiWithEditValidationError(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(1);
    
    // Open edit modal
    await page.click('ul.activity-list li:first-child button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Change BPM to invalid value
    await page.fill('#edit-avgBpm', '10');
    
    // Submit form
    await page.click('#edit-save');
    
    // Modal should stay open with error message
    await expect(page.locator('#edit-modal')).toBeVisible();
    await expect(page.locator('#edit-error')).toBeVisible();
    await expect(page.locator('#edit-error')).toContainText('Heart rate must be at least 20 BPM');
  });

  test('distance field hidden for Rowing activity type', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Click edit on the Rowing activity (second item)
    await page.click('ul.activity-list li:nth-child(2) button.action-btn.edit');
    await expect(page.locator('#edit-modal')).toBeVisible();
    
    // Distance field should be hidden for Rowing
    await expect(page.locator('#edit-distance-group')).toBeHidden();
  });
});

// Delete Activity Tests
test.describe('Delete Activity', () => {
  test('delete button opens confirmation dialog', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Click delete button on first activity
    await page.click('ul.activity-list li:first-child button.action-btn.delete');
    
    // Verify confirmation dialog is visible
    await expect(page.locator('#delete-dialog')).toBeVisible();
    await expect(page.locator('#delete-dialog-title')).toContainText('Delete Activity?');
  });

  test('delete confirmation can be cancelled', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open delete dialog
    await page.click('ul.activity-list li:first-child button.action-btn.delete');
    await expect(page.locator('#delete-dialog')).toBeVisible();
    
    // Click cancel button
    await page.click('#delete-cancel');
    
    // Dialog should be hidden
    await expect(page.locator('#delete-dialog')).toBeHidden();
    
    // Activity should still be in the list
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
  });

  test('delete confirmation closes on Escape key', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open delete dialog
    await page.click('ul.activity-list li:first-child button.action-btn.delete');
    await expect(page.locator('#delete-dialog')).toBeVisible();
    
    // Press Escape
    await page.keyboard.press('Escape');
    
    // Dialog should be hidden
    await expect(page.locator('#delete-dialog')).toBeHidden();
  });

  test('confirming delete shows success notification', async ({ page }) => {
    await mockApi(page);
    await page.goto('/pages/history.html');
    
    await expect(page.locator('ul.activity-list li')).toHaveCount(2);
    
    // Open delete dialog
    await page.click('ul.activity-list li:first-child button.action-btn.delete');
    await expect(page.locator('#delete-dialog')).toBeVisible();
    
    // Click confirm button
    await page.click('#delete-confirm');
    
    // Dialog should close and success notification should appear
    await expect(page.locator('#delete-dialog')).toBeHidden();
    await expect(page.locator('.notice.success')).toContainText('Activity deleted successfully');
  });
});
