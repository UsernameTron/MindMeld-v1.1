import { test, expect } from '@playwright/test';

test('login redirects to dashboard (mocked)', async ({ page }) => {
  // Intercept the auth request and return a fake token + user payload
  await page.route('**/api/auth/token', route =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        token: 'mock-jwt-token',
        refreshToken: 'mock-refresh-token',
        user: {
          id: '123',
          email: 'testuser@example.com',
          name: 'Test User',
          passwordChangeRequired: false,
          isVerified: true,
          lastLogin: '2025-05-12T00:00:00.000Z',
          role: 'user',
        },
      }),
    })
  );

  // Drive the login UI
  await page.goto('/login');
  await page.fill('input[name="email"]', 'testuser@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Wait for the redirect to /dashboard
  await page.waitForURL('**/dashboard');
  await expect(page).toHaveURL(/\/dashboard$/);
});
