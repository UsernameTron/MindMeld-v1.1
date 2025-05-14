import { test, expect } from '@playwright/test';
import { mockApiResponses } from './setup/mocks';

// Test authentication flow
test('Authentication Flow: login → refresh → protected route', async ({ page, context }) => {
  // Set up API mocks
  await mockApiResponses(page);
  
  // 1. Start at login page
  await page.goto('/login');
  await expect(page).toHaveURL('/login');
  
  // 2. Fill login form and submit
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // 3. Should redirect to dashboard after login
  await page.waitForURL('/dashboard');
  await expect(page).toHaveURL('/dashboard');
  
  // 4. Check cookies - should have HTTPOnly cookies set
  const cookies = await context.cookies();
  const authCookie = cookies.find(c => c.name === 'auth_token');
  const refreshCookie = cookies.find(c => c.name === 'refresh_token');
  
  expect(authCookie).toBeDefined();
  expect(refreshCookie).toBeDefined();
  expect(authCookie?.httpOnly).toBeTruthy();
  expect(refreshCookie?.httpOnly).toBeTruthy();
});

// Test token refresh
test('Token refresh: expired session should renew silently', async ({ page, context }) => {
  // Set up API mocks with a short-lived token
  await mockApiResponses(page, { tokenExpiresIn: 2 }); // Token expires in 2 seconds
  
  // 1. Log in
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Should redirect to dashboard
  await page.waitForURL('/dashboard');
  
  // 2. Wait for token to expire
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // 3. Navigate to another protected route
  await page.goto('/analyze');
  
  // 4. Should still be authenticated (token refreshed silently)
  await expect(page).toHaveURL('/analyze');
  
  // 5. Check for new auth cookie (refresh would have created a new one)
  const cookies = await context.cookies();
  const authCookie = cookies.find(c => c.name === 'auth_token');
  expect(authCookie).toBeDefined();
});

// Test tampered cookies
test('Tampered cookies should fail authentication', async ({ page, context }) => {
  // Set up API mocks
  await mockApiResponses(page);
  
  // 1. Log in
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Should redirect to dashboard
  await page.waitForURL('/dashboard');
  
  // 2. Manually set a tampered cookie
  await context.addCookies([
    {
      name: 'auth_token',
      value: 'tampered-token',
      domain: 'localhost',
      path: '/',
    }
  ]);
  
  // 3. Navigate to another protected route
  await page.goto('/analyze');
  
  // 4. Should be redirected to login
  await page.waitForURL('/login');
  await expect(page).toHaveURL('/login');
});

// Test CORS proxy
test('CORS proxy should forward requests to external API', async ({ page }) => {
  // Set up API mocks
  await mockApiResponses(page);
  
  // 1. Log in
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Should redirect to dashboard
  await page.waitForURL('/dashboard');
  
  // 2. Make a request to the proxy endpoint
  const response = await page.evaluate(async () => {
    const res = await fetch('/api/proxy/librechat/models', {
      method: 'GET',
      credentials: 'include',
    });
    return await res.json();
  });
  
  // 3. Should get a response from the proxy
  expect(response).toBeDefined();
});