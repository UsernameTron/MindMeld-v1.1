// e2e/playwright/security-flows.spec.ts
import { test, expect } from '@playwright/test';

// Test logout flow

test('logout clears session and redirects to login', async ({ page, context }) => {
  // Login first
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');

  // Click logout button
  await page.click('[data-testid="logout-button"]');
  await page.waitForURL('/login');
  await expect(page).toHaveURL('/login');

  // Should not be able to access dashboard
  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login');
});

// Test session timeout (simulate by clearing cookies)
test('session timeout redirects to login', async ({ page, context }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');

  // Simulate session timeout
  await context.clearCookies();
  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login');
});

// Multi-tab logout propagation
test('logout in one tab logs out other tabs', async ({ browser }) => {
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();
  const pageA = await contextA.newPage();
  const pageB = await contextB.newPage();

  // Login in both tabs
  await pageA.goto('/login');
  await pageA.fill('input[name="email"]', 'test@example.com');
  await pageA.fill('input[name="password"]', 'password123');
  await pageA.click('button[type="submit"]');
  await pageA.waitForURL('/dashboard');

  await pageB.goto('/login');
  await pageB.fill('input[name="email"]', 'test@example.com');
  await pageB.fill('input[name="password"]', 'password123');
  await pageB.click('button[type="submit"]');
  await pageB.waitForURL('/dashboard');

  // Logout in tab A
  await pageA.click('[data-testid="logout-button"]');
  await pageA.waitForURL('/login');

  // Tab B should also be logged out on next navigation
  await pageB.goto('/dashboard');
  await pageB.waitForURL('/login');
  await expect(pageB).toHaveURL('/login');

  await contextA.close();
  await contextB.close();
});

// Error scenario: invalid token
test('invalid token redirects to login', async ({ page, context }) => {
  // Set an invalid token manually
  await context.addCookies([{ name: 'token', value: 'invalid', url: 'http://localhost:3000', path: '/' }]);
  await page.goto('/dashboard');
  await page.waitForURL('/login');
  await expect(page).toHaveURL('/login');
});
