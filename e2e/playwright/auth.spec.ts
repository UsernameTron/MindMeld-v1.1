// moved from e2e/
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('login → dashboard → token refresh → protected route', async ({ page, context }) => {
    // Navigate to login
    await page.goto('/login');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();

    // Perform login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await page.waitForURL('/dashboard');
    await expect(page.locator('[data-testid="data-container"]')).toContainText('Hello from the API!');

    // Force token expiry by manipulating cookie
    const cookies = await context.cookies();
    const authCookie = cookies.find(c => c.name === 'token');
    if (authCookie) {
      await context.addCookies([{
        ...authCookie,
        expires: Math.floor(Date.now() / 1000) - 10 // Expired 10s ago
      }]);
    }

    // Click refresh button to trigger /auth/refresh
    await page.click('[data-testid="refresh-data"]');
    await page.waitForSelector('[data-testid="data-container"]:has-text("Hello from the API!")');

    // Verify still on dashboard
    await expect(page).toHaveURL('/dashboard');

    // Test protected route redirect when not logged in
    await context.clearCookies();
    await page.goto('/dashboard');
    await page.waitForURL('/login');
    await expect(page).toHaveURL('/login');
  });
});
