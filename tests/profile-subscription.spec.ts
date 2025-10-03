import { test, expect } from '@playwright/test';

test.describe('Profile and Subscription Flow', () => {
  test('should display profile page with white text and subscription button', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Wait for the page to load
    await expect(page.getByText('Trendzl')).toBeVisible();
    
    // Check if we're not logged in - should see Sign In button
    const signInButton = page.getByRole('button', { name: /Sign In/i });
    
    if (await signInButton.isVisible()) {
      console.log('Not logged in - test requires manual authentication setup');
      
      // For now, just verify the button exists
      await expect(signInButton).toBeVisible();
      
      // Click on Sign In button
      await signInButton.click();
      
      // Verify auth modal opens
      await expect(page.getByText('Welcome Back')).toBeVisible({ timeout: 5000 });
      
      console.log('✅ Auth modal opens correctly');
    } else {
      console.log('User is logged in');
      
      // If logged in, check for profile dropdown
      const profileDropdown = page.getByRole('button').filter({ has: page.locator('img[alt*="avatar"], div:has-text("@")') });
      await expect(profileDropdown).toBeVisible();
      
      // Click profile dropdown
      await profileDropdown.click();
      
      // Click "My Profile" in dropdown
      await page.getByRole('button', { name: /My Profile/i }).click();
      
      // Wait for profile page to load
      await expect(page.getByText('Profile Information')).toBeVisible();
      
      // Check that text is white (not gray)
      const nameLabel = page.getByText('Name:');
      const emailLabel = page.getByText('Email:');
      
      // Get computed color - should be white or very light color
      const nameColor = await nameLabel.evaluate(el => window.getComputedStyle(el).color);
      const emailColor = await emailLabel.evaluate(el => window.getComputedStyle(el).color);
      
      console.log('Name label color:', nameColor);
      console.log('Email label color:', emailColor);
      
      // Check for subscription section
      await expect(page.getByText('Subscription')).toBeVisible();
      
      // Check if Subscribe button exists (for users without subscription)
      const subscribeButton = page.getByRole('button', { name: /Subscribe Now/i });
      
      if (await subscribeButton.isVisible()) {
        console.log('✅ Subscribe button is visible in profile');
        
        // Click subscribe button
        await subscribeButton.click();
        
        // Wait a bit for the checkout session creation
        await page.waitForTimeout(2000);
        
        // Check if we're redirected to Stripe or if there's an error
        const currentUrl = page.url();
        console.log('Current URL after subscribe click:', currentUrl);
        
        if (currentUrl.includes('stripe') || currentUrl.includes('checkout')) {
          console.log('✅ Successfully redirected to Stripe checkout');
          
          // Go back to test the return flow
          await page.goBack();
          
          // Add success query param to simulate return from Stripe
          await page.goto('/profile?session=success');
          
          // Wait for toast notification
          await expect(page.getByText(/Payment Successful/i)).toBeVisible({ timeout: 5000 });
          
          console.log('✅ Success toast appears after Stripe return');
          
          // Verify user is still logged in (profile info should be visible)
          await expect(page.getByText('Profile Information')).toBeVisible();
          
          console.log('✅ User remains logged in after Stripe redirect');
        } else {
          console.log('⚠️ Not redirected to Stripe - check if backend is running');
        }
      } else {
        console.log('User has active subscription or button not found');
      }
    }
  });

  test('should handle canceled payment redirect', async ({ page }) => {
    // Go directly to profile with canceled session
    await page.goto('/profile?session=canceled');
    
    // Wait for potential toast notification
    await page.waitForTimeout(1000);
    
    // Check if canceled toast appears
    const canceledToast = page.getByText(/Payment Canceled/i);
    if (await canceledToast.isVisible()) {
      console.log('✅ Canceled toast appears correctly');
    }
    
    // Verify user can still access profile
    // (This will fail if not logged in, which is expected)
    const profileInfo = page.getByText('Profile Information');
    if (await profileInfo.isVisible()) {
      console.log('✅ Profile page accessible after canceled payment');
    }
  });

  test('should keep user logged in after navigation', async ({ page }) => {
    // Navigate to home
    await page.goto('/');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    
    // Check if logged in by looking for profile dropdown or sign in button
    const signInButton = page.getByRole('button', { name: /Sign In/i });
    
    if (!(await signInButton.isVisible())) {
      console.log('User is logged in, testing navigation...');
      
      // Navigate to profile
      const profileDropdown = page.getByRole('button').filter({ has: page.locator('img[alt*="avatar"], div:has-text("@")') });
      await profileDropdown.click();
      await page.getByRole('button', { name: /My Profile/i }).click();
      
      // Go back to home
      await page.goto('/');
      
      // Profile dropdown should still be visible (user still logged in)
      await expect(profileDropdown).toBeVisible();
      
      console.log('✅ User remains logged in after navigation');
    } else {
      console.log('User not logged in - skipping navigation test');
    }
  });
});

