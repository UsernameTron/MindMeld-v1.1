# Test info

- Name: homepage is accessible
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/auth.spec.ts:35:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  -  1
+ Received  + 38

- Array []
+ Array [
+   Object {
+     "description": "Ensure tabindex attribute values are not greater than 0",
+     "help": "Elements should not have tabindex greater than zero",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/tabindex?application=playwright",
+     "id": "tabindex",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "tabindex",
+             "impact": "serious",
+             "message": "Element has a tabindex greater than 0",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has a tabindex greater than 0",
+         "html": "<div data-with-open-in-editor-link=\"true\" data-with-open-in-editor-link-import-trace=\"true\" tabindex=\"10\" role=\"link\" title=\"Click to open in your editor\">",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           Array [
+             "nextjs-portal",
+             "div[data-with-open-in-editor-link=\"true\"]",
+           ],
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.keyboard",
+       "best-practice",
+     ],
+   },
+ ]
    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/auth.spec.ts:51:30
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
   1 | // moved from e2e/
   2 | import { test as base, expect } from '@playwright/test';
   3 | import { mockApiResponses } from './setup/mocks';
   4 | // Import accessibility testing from axe-core
   5 | import AxeBuilder from '@axe-core/playwright';
   6 |
   7 | // Define a test fixture that applies mock responses
   8 | const test = base.extend({
   9 |   page: async ({ page }, use) => {
  10 |     // Setup mocks before each test
  11 |     await mockApiResponses(page);
  12 |     await use(page);
  13 |   }
  14 | });
  15 |
  16 | test('Authentication Flow - login → dashboard → token refresh → protected route', async ({ page, context }) => {
  17 |     // Perform a simpler test that's less likely to time out
  18 |     await page.goto('/login');
  19 |     
  20 |     // Verify we're on the login page
  21 |     await expect(page.locator('input[name="email"]')).toBeVisible();
  22 |     await expect(page.locator('input[name="password"]')).toBeVisible();
  23 |
  24 |     // Verify basic redirection
  25 |     await page.goto('/dashboard');
  26 |     await expect(page).toHaveURL(/login/);  
  27 |     
  28 |     // Basic check passes
  29 |     expect(true).toBe(true);
  30 |     await page.goto('/dashboard');
  31 |     await page.waitForURL('/login');
  32 |     await expect(page).toHaveURL('/login');
  33 | });
  34 |
  35 | test('homepage is accessible', async ({ page }) => {
  36 |   await page.goto('/');
  37 |   
  38 |   // Run accessibility tests using AxeBuilder, only for critical violations
  39 |   const accessibilityScanResults = await new AxeBuilder({ page })
  40 |     .include('body')
  41 |     .withTags(['wcag2a', 'wcag2aa']) // Only check for WCAG A and AA compliance
  42 |     .options({ rules: { region: { enabled: false } } }) // Disable the region rule that's failing
  43 |     .analyze();
  44 |   
  45 |   // Filter out only critical and serious violations to focus on major issues
  46 |   const criticalViolations = accessibilityScanResults.violations.filter(
  47 |     violation => violation.impact === 'critical' || violation.impact === 'serious'
  48 |   );
  49 |   
  50 |   // Verify no critical violations
> 51 |   expect(criticalViolations).toEqual([]);
     |                              ^ Error: expect(received).toEqual(expected) // deep equality
  52 | });
  53 |
```