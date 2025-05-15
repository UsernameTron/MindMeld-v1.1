# Test info

- Name: deepResearch template UI (desktop) >> renders template selection for deepResearch
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-visual.spec.ts:25:11

# Error details

```
TimeoutError: page.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid="template-select"]')

    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-visual.spec.ts:27:20
```

# Page snapshot

```yaml
- heading "MindMeld Login" [level=1]
- paragraph: Enter your credentials to access the platform
- text: Email address
- textbox "Email address": test@example.com
- text: Password
- textbox "Password": Test123!
- button "Sign in"
- text: (Test credentials are pre-filled)
- alert
- button "Open Next.js Dev Tools":
  - img
- button "Open issues overlay": 1 Issue
- button "Collapse issues badge":
  - img
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
- dialog "Runtime Error":
  - text: Runtime Error
  - button "Copy Stack Trace":
    - img
  - button "No related documentation found" [disabled]:
    - img
  - link "Learn more about enabling Node.js inspector for server code with Chrome DevTools":
    - /url: https://nextjs.org/docs/app/building-your-application/configuring/debugging#server-side-code
    - img
  - paragraph: "SyntaxError: Unexpected token '<', \"<!DOCTYPE \"... is not valid JSON"
```

# Test source

```ts
   1 | // Playwright UI visual regression and responsive tests for MindMeld templates
   2 | // This suite is separate from integration tests for maintainability
   3 |
   4 | import { test, expect } from '@playwright/test';
   5 |
   6 | const viewports = [
   7 |   { name: 'desktop', width: 1280, height: 800 },
   8 |   { name: 'tablet', width: 768, height: 1024 },
   9 |   { name: 'mobile', width: 375, height: 667 },
  10 | ];
  11 |
  12 | const templates = [
  13 |   'deepResearch',
  14 |   'advancedReasoning',
  15 |   'counterfactual',
  16 |   'satiricalVoice',
  17 |   'pentagramVisual',
  18 | ];
  19 |
  20 | for (const viewport of viewports) {
  21 |   for (const template of templates) {
  22 |     test.describe(`${template} template UI (${viewport.name})`, () => {
  23 |       test.use({ viewport: { width: viewport.width, height: viewport.height } });
  24 |
  25 |       test(`renders template selection for ${template}`, async ({ page }) => {
  26 |         await page.goto('/');
> 27 |         await page.click(`[data-testid="template-select"]`);
     |                    ^ TimeoutError: page.click: Timeout 30000ms exceeded.
  28 |         await page.click(`[data-testid="template-option-${template}"]`);
  29 |         await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
  30 |         await page.screenshot({ path: `screenshots/${template}-selection-${viewport.name}.png` });
  31 |       });
  32 |
  33 |       test(`renders parameter form for ${template}`, async ({ page }) => {
  34 |         await page.goto('/');
  35 |         await page.click(`[data-testid="template-select"]`);
  36 |         await page.click(`[data-testid="template-option-${template}"]`);
  37 |         await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
  38 |         await page.screenshot({ path: `screenshots/${template}-form-${viewport.name}.png` });
  39 |       });
  40 |
  41 |       test(`renders prompt display for ${template}`, async ({ page }) => {
  42 |         await page.goto('/');
  43 |         await page.click(`[data-testid="template-select"]`);
  44 |         await page.click(`[data-testid="template-option-${template}"]`);
  45 |         await page.fill(`[data-testid="template-form-${template}"] input`, 'test input');
  46 |         await page.click(`[data-testid="generate-prompt-btn"]`);
  47 |         await expect(page.locator(`[data-testid="prompt-display"]`)).toBeVisible();
  48 |         await page.screenshot({ path: `screenshots/${template}-prompt-${viewport.name}.png` });
  49 |       });
  50 |     });
  51 |   }
  52 | }
  53 |
```