# Test info

- Name: CORS proxy should forward requests to external API
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/auth-flow.spec.ts:95:5

# Error details

```
TimeoutError: page.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator('input[name="email"]')

    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/auth-flow.spec.ts:101:14
```

# Page snapshot

```yaml
- alert
- button "Open Next.js Dev Tools":
  - img
- button "Open issues overlay": 1 Issue
- navigation:
  - button "previous" [disabled]:
    - img "previous"
  - text: 1/1
  - button "next" [disabled]:
    - img "next"
- img
- img
- text: Next.js 15.3.2 Webpack
- img
- dialog "Build Error":
  - text: Build Error
  - button "Copy Stack Trace":
    - img
  - link "Go to related documentation":
    - /url: https://nextjs.org/docs/messages/module-not-found
    - img
  - link "Learn more about enabling Node.js inspector for server code with Chrome DevTools":
    - /url: https://nextjs.org/docs/app/building-your-application/configuring/debugging#server-side-code
    - img
  - paragraph: "Module not found: Can't resolve '@/components/ui/atoms/Button'"
  - img
  - text: ./src/components/ui/molecules/AnalyzerSettings/AnalyzerSettings.tsx (8:1)
  - button "Open in editor":
    - img
  - text: "Module not found: Can't resolve '@/components/ui/atoms/Button' 6 | import { LoadingIndicator } from '@/components/ui/molecules/LoadingIndicator/LoadingIndicator'; 7 | import { ErrorDisplay } from '@/components/ui/molecules/ErrorDisplay/ErrorDisplay'; > 8 | import { Button } from '@/components/ui/atoms/Button'; | ^ 9 | import { cn } from '@/utils/cn'; 10 | 11 | interface AnalyzerSettingsProps {"
  - link "https://nextjs.org/docs/messages/module-not-found":
    - /url: https://nextjs.org/docs/messages/module-not-found
  - text: "Import trace for requested module:"
  - link "./pages/analyze/index.tsx":
    - text: ./pages/analyze/index.tsx
    - img
- contentinfo:
  - paragraph: This error occurred during the build process and can only be dismissed by fixing the error.
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 | import { mockApiResponses } from './setup/mocks';
   3 |
   4 | // Test authentication flow
   5 | test('Authentication Flow: login → refresh → protected route', async ({ page, context }) => {
   6 |   // Set up API mocks
   7 |   await mockApiResponses(page);
   8 |   
   9 |   // 1. Start at login page
   10 |   await page.goto('/login');
   11 |   await expect(page).toHaveURL('/login');
   12 |   
   13 |   // 2. Fill login form and submit
   14 |   await page.fill('input[name="email"]', 'test@example.com');
   15 |   await page.fill('input[name="password"]', 'password123');
   16 |   await page.click('button[type="submit"]');
   17 |   
   18 |   // 3. Should redirect to dashboard after login
   19 |   await page.waitForURL('/dashboard');
   20 |   await expect(page).toHaveURL('/dashboard');
   21 |   
   22 |   // 4. Check cookies - should have HTTPOnly cookies set
   23 |   const cookies = await context.cookies();
   24 |   const authCookie = cookies.find(c => c.name === 'auth_token');
   25 |   const refreshCookie = cookies.find(c => c.name === 'refresh_token');
   26 |   
   27 |   expect(authCookie).toBeDefined();
   28 |   expect(refreshCookie).toBeDefined();
   29 |   expect(authCookie?.httpOnly).toBeTruthy();
   30 |   expect(refreshCookie?.httpOnly).toBeTruthy();
   31 | });
   32 |
   33 | // Test token refresh
   34 | test('Token refresh: expired session should renew silently', async ({ page, context }) => {
   35 |   // Set up API mocks with a short-lived token
   36 |   await mockApiResponses(page, { tokenExpiresIn: 2 }); // Token expires in 2 seconds
   37 |   
   38 |   // 1. Log in
   39 |   await page.goto('/login');
   40 |   await page.fill('input[name="email"]', 'test@example.com');
   41 |   await page.fill('input[name="password"]', 'password123');
   42 |   await page.click('button[type="submit"]');
   43 |   
   44 |   // Should redirect to dashboard
   45 |   await page.waitForURL('/dashboard');
   46 |   
   47 |   // 2. Wait for token to expire
   48 |   await new Promise(resolve => setTimeout(resolve, 3000));
   49 |   
   50 |   // 3. Navigate to another protected route
   51 |   await page.goto('/analyze');
   52 |   
   53 |   // 4. Should still be authenticated (token refreshed silently)
   54 |   await expect(page).toHaveURL('/analyze');
   55 |   
   56 |   // 5. Check for new auth cookie (refresh would have created a new one)
   57 |   const cookies = await context.cookies();
   58 |   const authCookie = cookies.find(c => c.name === 'auth_token');
   59 |   expect(authCookie).toBeDefined();
   60 | });
   61 |
   62 | // Test tampered cookies
   63 | test('Tampered cookies should fail authentication', async ({ page, context }) => {
   64 |   // Set up API mocks
   65 |   await mockApiResponses(page);
   66 |   
   67 |   // 1. Log in
   68 |   await page.goto('/login');
   69 |   await page.fill('input[name="email"]', 'test@example.com');
   70 |   await page.fill('input[name="password"]', 'password123');
   71 |   await page.click('button[type="submit"]');
   72 |   
   73 |   // Should redirect to dashboard
   74 |   await page.waitForURL('/dashboard');
   75 |   
   76 |   // 2. Manually set a tampered cookie
   77 |   await context.addCookies([
   78 |     {
   79 |       name: 'auth_token',
   80 |       value: 'tampered-token',
   81 |       domain: 'localhost',
   82 |       path: '/',
   83 |     }
   84 |   ]);
   85 |   
   86 |   // 3. Navigate to another protected route
   87 |   await page.goto('/analyze');
   88 |   
   89 |   // 4. Should be redirected to login
   90 |   await page.waitForURL('/login');
   91 |   await expect(page).toHaveURL('/login');
   92 | });
   93 |
   94 | // Test CORS proxy
   95 | test('CORS proxy should forward requests to external API', async ({ page }) => {
   96 |   // Set up API mocks
   97 |   await mockApiResponses(page);
   98 |   
   99 |   // 1. Log in
  100 |   await page.goto('/login');
> 101 |   await page.fill('input[name="email"]', 'test@example.com');
      |              ^ TimeoutError: page.fill: Timeout 30000ms exceeded.
  102 |   await page.fill('input[name="password"]', 'password123');
  103 |   await page.click('button[type="submit"]');
  104 |   
  105 |   // Should redirect to dashboard
  106 |   await page.waitForURL('/dashboard');
  107 |   
  108 |   // 2. Make a request to the proxy endpoint
  109 |   const response = await page.evaluate(async () => {
  110 |     const res = await fetch('/api/proxy/librechat/models', {
  111 |       method: 'GET',
  112 |       credentials: 'include',
  113 |     });
  114 |     return await res.json();
  115 |   });
  116 |   
  117 |   // 3. Should get a response from the proxy
  118 |   expect(response).toBeDefined();
  119 | });
```