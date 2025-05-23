# Test info

- Name: should login successfully with valid credentials
- Location: /Users/cpconnor/projects/mindmeld-v1.1/e2e/playwright/tests/auth/login.spec.ts:4:1

# Error details

```
Error: page.fill: Test ended.
Call log:
  - waiting for locator('[data-testid="email-input"]')

    at /Users/cpconnor/projects/mindmeld-v1.1/e2e/playwright/tests/auth/login.spec.ts:6:14
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | // Base test for successful login
   4 | test('should login successfully with valid credentials', async ({ page }) => {
   5 |   await page.goto('/login');
>  6 |   await page.fill('[data-testid="email-input"]', 'test@example.com');
     |              ^ Error: page.fill: Test ended.
   7 |   await page.fill('[data-testid="password-input"]', 'Test123!');
   8 |   await page.click('[data-testid="login-button"]');
   9 |   await expect(page).toHaveURL('/dashboard');
   10 |   await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
   11 | });
   12 |
   13 | // Test for account lockout after failed login attempts
   14 | test('should lock account after multiple failed login attempts', async ({ page }) => {
   15 |   await page.goto('/login');
   16 |
   17 |   // Attempt to login with incorrect password multiple times
   18 |   for (let i = 0; i < 5; i++) {
   19 |     await page.fill('[data-testid="email-input"]', 'test@example.com');
   20 |     await page.fill('[data-testid="password-input"]', `wrong-password-${i}`);
   21 |     await page.click('[data-testid="login-button"]');
   22 |
   23 |     if (i < 4) {
   24 |       // For attempts 1-4, should see remaining attempts message
   25 |       await expect(page.locator('[data-testid="login-error"]')).toContainText('login attempts remaining');
   26 |     }
   27 |   }
   28 |
   29 |   // After 5 failures, account should be locked
   30 |   await expect(page.locator('[data-testid="login-error"]')).toContainText('Account is locked');
   31 |   await expect(page.locator('[data-testid="login-error"]')).toContainText('Try again in');
   32 | });
   33 |
   34 | // Test password reset flow
   35 | test('should complete password reset flow', async ({ page }) => {
   36 |   // Step 1: Go to login page and click forgot password
   37 |   await page.goto('/login');
   38 |   await page.click('[data-testid="forgot-password-link"]');
   39 |   await expect(page).toHaveURL('/forgot-password');
   40 |
   41 |   // Step 2: Submit forgot password form
   42 |   await page.fill('[data-testid="email-input"]', 'test@example.com');
   43 |   await page.click('[data-testid="forgot-password-button"]');
   44 |
   45 |   // Should see confirmation message
   46 |   await expect(page.locator('[data-testid="success-message"]')).toContainText('reset link will be sent');
   47 |
   48 |   // In development environment, should see debug reset link
   49 |   const resetLink = await page.locator('[data-testid="debug-reset-link"]').getAttribute('href');
   50 |   expect(resetLink).toContain('/reset-password?token=');
   51 |
   52 |   // Step 3: Follow the reset link
   53 |   await page.goto(resetLink);
   54 |   await expect(page).toHaveURL(/\/reset-password\?token=/);
   55 |
   56 |   // Step 4: Submit new password
   57 |   await page.fill('[data-testid="new-password-input"]', 'NewSecurePassword123!');
   58 |   await page.fill('[data-testid="confirm-password-input"]', 'NewSecurePassword123!');
   59 |   await page.click('[data-testid="reset-password-button"]');
   60 |
   61 |   // Should see success message
   62 |   await expect(page.locator('[data-testid="success-message"]')).toContainText('Password has been reset successfully');
   63 |
   64 |   // Should redirect to login page after a delay
   65 |   await page.waitForURL('/login');
   66 |
   67 |   // Step 5: Login with new password
   68 |   await page.fill('[data-testid="email-input"]', 'test@example.com');
   69 |   await page.fill('[data-testid="password-input"]', 'NewSecurePassword123!');
   70 |   await page.click('[data-testid="login-button"]');
   71 |
   72 |   // Should login successfully
   73 |   await expect(page).toHaveURL('/dashboard');
   74 | });
   75 |
   76 | // Full authentication flow from registration to logout
   77 | test('should complete full authentication flow', async ({ page }) => {
   78 |   // Step 1: Register a new account (if registration is implemented)
   79 |   // If no registration exists, we'll use test account
   80 |
   81 |   // Step 2: Login
   82 |   await page.goto('/login');
   83 |   await page.fill('[data-testid="email-input"]', 'test@example.com');
   84 |   await page.fill('[data-testid="password-input"]', 'Test123!');
   85 |   await page.click('[data-testid="login-button"]');
   86 |   await expect(page).toHaveURL('/dashboard');
   87 |
   88 |   // Step 3: Access protected resource
   89 |   await page.goto('/dashboard');
   90 |   await expect(page).toHaveURL('/dashboard'); // Shouldn't redirect to login
   91 |
   92 |   // Step 4: Check profile/user info if available
   93 |   await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
   94 |
   95 |   // Step 5: Logout
   96 |   await page.click('[data-testid="logout-button"]');
   97 |
   98 |   // Should redirect to login page
   99 |   await expect(page).toHaveURL('/login');
  100 |
  101 |   // Step 6: Verify cannot access protected resources after logout
  102 |   await page.goto('/dashboard');
  103 |
  104 |   // Should be redirected back to login
  105 |   await expect(page).toHaveURL('/login');
  106 | });
```
