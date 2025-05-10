// moved from e2e/
import { test, expect } from '@playwright/test';

test('blocks access to protected route when not authenticated', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/login/);
});

test('sets HttpOnly and Secure flags on auth cookies', async ({ page, context }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');

  const cookies = await context.cookies();
  const authCookie = cookies.find(c => c.name === 'auth_token');
  expect(authCookie).toBeDefined();
  expect(authCookie?.httpOnly).toBe(true);
  const shouldBeSecure = process.env.NODE_ENV === 'production' || process.env.FORCE_SECURE === 'true';
  expect(authCookie?.secure).toBe(shouldBeSecure);
});
