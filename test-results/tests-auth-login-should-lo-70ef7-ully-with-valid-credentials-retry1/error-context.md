# Test info

- Name: should login successfully with valid credentials
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/auth/login.spec.ts:3:5

# Error details

```
TimeoutError: page.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid="email-input"]')

    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/auth/login.spec.ts:5:14
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
   2 |
   3 | test('should login successfully with valid credentials', async ({ page }) => {
   4 |   await page.goto('/login');
>  5 |   await page.fill('[data-testid="email-input"]', 'test@example.com');
     |              ^ TimeoutError: page.fill: Timeout 30000ms exceeded.
   6 |   await page.fill('[data-testid="password-input"]', 'password123');
   7 |   await page.click('[data-testid="login-button"]');
   8 |   await expect(page).toHaveURL('/dashboard');
   9 |   await expect(page.locator('[data-testid="user-profile"]')).toBeVisible();
  10 | });
  11 |
```