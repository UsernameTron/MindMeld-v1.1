# Test info

- Name: login redirects to dashboard (mocked)
- Location: /Users/cpconnor/projects/mindmeld-fresh/frontend/e2e/login.spec.ts:3:1

# Error details

```
Error: page.waitForURL: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/dashboard" until "load"
  navigated to "http://localhost:3000/login"
  navigated to "http://localhost:3000/login"
============================================================
    at /Users/cpconnor/projects/mindmeld-fresh/frontend/e2e/login.spec.ts:32:14
```

# Page snapshot

```yaml
- heading "Login" [level=1]
- text: Email
- textbox "Email"
- text: Password
- textbox "Password"
- button "Login"
- alert
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | test('login redirects to dashboard (mocked)', async ({ page }) => {
   4 |   // Intercept the auth request and return a fake token + user payload
   5 |   await page.route('**/api/auth/token', route =>
   6 |     route.fulfill({
   7 |       status: 200,
   8 |       contentType: 'application/json',
   9 |       body: JSON.stringify({
  10 |         token: 'mock-jwt-token',
  11 |         refreshToken: 'mock-refresh-token',
  12 |         user: {
  13 |           id: '123',
  14 |           email: 'testuser@example.com',
  15 |           name: 'Test User',
  16 |           passwordChangeRequired: false,
  17 |           isVerified: true,
  18 |           lastLogin: '2025-05-12T00:00:00.000Z',
  19 |           role: 'user',
  20 |         },
  21 |       }),
  22 |     })
  23 |   );
  24 |
  25 |   // Drive the login UI
  26 |   await page.goto('/login');
  27 |   await page.fill('input[name="email"]', 'testuser@example.com');
  28 |   await page.fill('input[name="password"]', 'password123');
  29 |   await page.click('button[type="submit"]');
  30 |
  31 |   // Wait for the redirect to /dashboard
> 32 |   await page.waitForURL('**/dashboard');
     |              ^ Error: page.waitForURL: Test timeout of 30000ms exceeded.
  33 |   await expect(page).toHaveURL(/\/dashboard$/);
  34 | });
  35 |
```