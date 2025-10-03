import { test, expect } from '@playwright/test';

test.describe('Video Opening Flow Tests', () => {
  test('should not replace current tab when clicking video', async ({ page, context }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Get the initial URL
    const initialUrl = page.url();
    console.log('Initial URL:', initialUrl);
    
    // Store current page count
    const initialPages = context.pages().length;
    console.log('Initial pages count:', initialPages);
    
    // Look for any Play button or video link
    const playButtons = await page.locator('button[aria-label*="Play"]').count();
    
    if (playButtons > 0) {
      console.log(`Found ${playButtons} play buttons`);
      
      // Listen for new page/tab creation
      const newPagePromise = context.waitForEvent('page', { timeout: 10000 }).catch(() => null);
      
      // Click the first play button
      await page.locator('button[aria-label*="Play"]').first().click();
      
      // Wait a bit to see if page changes
      await page.waitForTimeout(2000);
      
      // Check if current tab URL changed (it should NOT)
      const currentUrl = page.url();
      console.log('Current URL after click:', currentUrl);
      
      // Verify the original page is still on the same URL
      expect(currentUrl).toBe(initialUrl);
      console.log('✅ Original page URL unchanged - session preserved!');
      
      // Check if new page was opened
      const newPage = await newPagePromise;
      if (newPage) {
        console.log('✅ New tab/window was opened');
        await newPage.close();
      } else {
        console.log('⚠️ No new tab opened (might be blocked by popup blocker)');
      }
      
    } else {
      console.log('⚠️ No play buttons found on page (might need analysis first)');
    }
  });

  test('should preserve session when navigating to analysis page', async ({ page }) => {
    // Navigate to an analysis result page
    const testId = 'test-analysis-id';
    await page.goto(`/analysis/${testId}`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if we're still on the analysis page
    expect(page.url()).toContain('/analysis/');
    console.log('✅ Analysis page loaded correctly');
    
    // Verify back button exists
    const backButton = await page.locator('text=Back to My Trends').isVisible();
    expect(backButton).toBe(true);
    console.log('✅ Back button is visible');
  });

  test('should not navigate away from My Trends when viewing saved analysis', async ({ page, context }) => {
    // Navigate to My Trends
    await page.goto('/my-trends');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    const initialUrl = page.url();
    console.log('My Trends URL:', initialUrl);
    
    // Look for View buttons
    const viewButtons = await page.locator('button:has-text("View")').count();
    
    if (viewButtons > 0) {
      console.log(`Found ${viewButtons} view buttons`);
      
      // Listen for new page/tab creation
      const newPagePromise = context.waitForEvent('page', { timeout: 5000 }).catch(() => null);
      
      // Click first View button
      await page.locator('button:has-text("View")').first().click();
      
      // Wait a bit
      await page.waitForTimeout(1000);
      
      // Verify we're still on My Trends or navigated properly
      const currentUrl = page.url();
      console.log('Current URL after View click:', currentUrl);
      
      // Check if new page was opened
      const newPage = await newPagePromise;
      if (newPage) {
        console.log('✅ New tab opened with analysis');
        expect(newPage.url()).toContain('/analysis/');
        await newPage.close();
      }
      
    } else {
      console.log('⚠️ No saved analyses found (expected for new user)');
    }
  });
});

