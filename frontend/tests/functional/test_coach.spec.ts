import { test, expect } from '@playwright/test';

/**
 * Functional tests for AI Coach recommendation feature.
 * 
 * Tests home page rendering of recommendation card, loading states,
 * and fallback behavior.
 */

const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:4280';

test.describe('AI Coach Recommendation', () => {
  
  test.describe('Home Page Recommendation Card', () => {
    
    test('should display recommendation card on home page', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Wait for recommendation card to appear
      const card = page.locator('[data-testid="recommendation-card"]');
      await expect(card).toBeVisible({ timeout: 10000 });
      
      // Check card structure
      await expect(card.locator('.recommendation-title')).toBeVisible();
      await expect(card.locator('.recommendation-workout')).toBeVisible();
      await expect(card.locator('.recommendation-rationale')).toBeVisible();
    });
    
    test('should display workout details in card', async ({ page }) => {
      await page.goto(BASE_URL);
      
      const card = page.locator('[data-testid="recommendation-card"]');
      await expect(card).toBeVisible({ timeout: 10000 });
      
      // Check workout type and duration are shown
      const workoutSection = card.locator('.recommendation-workout');
      await expect(workoutSection).toContainText(/Running|Cross-training|Rest|Strength/);
      await expect(workoutSection).toContainText(/minutes/i);
    });
    
    test('should display rationale text', async ({ page }) => {
      await page.goto(BASE_URL);
      
      const card = page.locator('[data-testid="recommendation-card"]');
      await expect(card).toBeVisible({ timeout: 10000 });
      
      const rationale = card.locator('.recommendation-rationale');
      const text = await rationale.textContent();
      expect(text).toBeTruthy();
      expect(text!.length).toBeGreaterThan(10);
    });
    
  });
  
  test.describe('Loading State', () => {
    
    test('should show loading skeleton while fetching', async ({ page }) => {
      // Slow down network to see loading state
      await page.route('**/api/coach/today', async route => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        await route.continue();
      });
      
      await page.goto(BASE_URL);
      
      // Loading skeleton should appear first
      const skeleton = page.locator('[data-testid="recommendation-loading"]');
      await expect(skeleton).toBeVisible();
      
      // Then recommendation card should replace it
      const card = page.locator('[data-testid="recommendation-card"]');
      await expect(card).toBeVisible({ timeout: 10000 });
    });
    
    test('should show loading text', async ({ page }) => {
      await page.route('**/api/coach/today', async route => {
        await new Promise(resolve => setTimeout(resolve, 500));
        await route.continue();
      });
      
      await page.goto(BASE_URL);
      
      // Check for loading text
      const loadingText = page.getByText(/generating|loading/i);
      await expect(loadingText).toBeVisible();
    });
    
  });
  
  test.describe('Fallback State', () => {
    
    test('should display fallback when API returns fallback', async ({ page }) => {
      // Mock API to return fallback response
      await page.route('**/api/coach/today', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            date: new Date().toISOString().split('T')[0],
            goal: 'half-marathon',
            title: 'Easy aerobic run',
            workout: {
              type: 'Running',
              durationMinutes: 45,
              details: [
                'Easy conversational pace for 35-45 minutes',
                'Focus on comfortable breathing',
                'Optional: 4-6 x 20s strides'
              ]
            },
            rationale: 'A moderate aerobic run is a safe default for maintaining fitness.',
            confidence: 'low',
            fallback: true
          })
        });
      });
      
      await page.goto(BASE_URL);
      
      const card = page.locator('[data-testid="recommendation-card"]');
      await expect(card).toBeVisible({ timeout: 10000 });
      
      // Check for fallback indicator
      const fallbackIndicator = card.locator('.recommendation-fallback');
      await expect(fallbackIndicator).toBeVisible();
    });
    
    test('should display error state when API fails', async ({ page }) => {
      // Mock API to fail
      await page.route('**/api/coach/today', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });
      
      await page.goto(BASE_URL);
      
      // Should show error state (which falls back to default recommendation)
      const errorOrFallback = page.locator('[data-testid="recommendation-card"], [data-testid="recommendation-error"]');
      await expect(errorOrFallback).toBeVisible({ timeout: 10000 });
    });
    
  });
  
});

test.describe('Recommendation Refresh After Activity', () => {
  
  test('should show success toast after activity save redirect', async ({ page }) => {
    // Simulate redirect from log-activity with toast data
    await page.goto(BASE_URL);
    
    // Set toast data in session storage (simulating redirect)
    await page.evaluate(() => {
      sessionStorage.setItem('fitapp_toast', JSON.stringify({
        type: 'success',
        message: 'Activity saved successfully!'
      }));
    });
    
    // Reload to trigger toast display
    await page.reload();
    
    // Toast should appear
    const toast = page.locator('.notification.success, .toast.success, [role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
  });
  
  test('should fetch fresh recommendation on page load', async ({ page }) => {
    let apiCallCount = 0;
    
    await page.route('**/api/coach/today', async route => {
      apiCallCount++;
      await route.continue();
    });
    
    await page.goto(BASE_URL);
    
    // Wait for recommendation to load
    const card = page.locator('[data-testid="recommendation-card"]');
    await expect(card).toBeVisible({ timeout: 10000 });
    
    // API should have been called
    expect(apiCallCount).toBeGreaterThan(0);
  });
  
  test('should refresh recommendation after navigation from log-activity', async ({ page }) => {
    let apiCallCount = 0;
    
    await page.route('**/api/coach/today', async route => {
      apiCallCount++;
      await route.continue();
    });
    
    // Start on log-activity page
    await page.goto(`${BASE_URL}/pages/log-activity.html`);
    
    // Navigate to home
    await page.click('a[href*="index.html"], .navbar-brand');
    
    // Wait for recommendation
    const card = page.locator('[data-testid="recommendation-card"]');
    await expect(card).toBeVisible({ timeout: 10000 });
    
    // API should have been called
    expect(apiCallCount).toBeGreaterThan(0);
  });
  
});
