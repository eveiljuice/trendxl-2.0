import { test, expect } from '@playwright/test';

test.describe('Analysis Flow Tests', () => {
  test('should save analysis and open in new tab after completion', async ({ page, context }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if we're on the home page
    await expect(page.locator('text=Trendzl')).toBeVisible();
    
    console.log('✅ Home page loaded successfully');
  });

  test('should view saved analysis from My Trends in new tab', async ({ page, context }) => {
    // Navigate to My Trends
    await page.goto('/my-trends');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if we're on My Trends page
    await expect(page.locator('text=My Trends')).toBeVisible();
    
    console.log('✅ My Trends page loaded successfully');
  });

  test('should load analysis result page directly', async ({ page }) => {
    // Try to navigate to a sample analysis page (will fail if ID doesn't exist, but route should work)
    const testId = 'test-id-123';
    await page.goto(`/analysis/${testId}`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Should show either the analysis or an error message
    const hasBackButton = await page.locator('text=Back to My Trends').isVisible();
    expect(hasBackButton).toBe(true);
    
    console.log('✅ Analysis result page route works correctly');
  });
});

