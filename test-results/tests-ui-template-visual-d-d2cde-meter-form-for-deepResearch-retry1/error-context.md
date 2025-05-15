# Test info

- Name: deepResearch template UI (desktop) >> renders parameter form for deepResearch
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-visual.spec.ts:33:11

# Error details

```
Error: page.click: Target page, context or browser has been closed
Call log:
  - waiting for locator('[data-testid="template-select"]')

    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-visual.spec.ts:35:20
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
  27 |         await page.click(`[data-testid="template-select"]`);
  28 |         await page.click(`[data-testid="template-option-${template}"]`);
  29 |         await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
  30 |         await page.screenshot({ path: `screenshots/${template}-selection-${viewport.name}.png` });
  31 |       });
  32 |
  33 |       test(`renders parameter form for ${template}`, async ({ page }) => {
  34 |         await page.goto('/');
> 35 |         await page.click(`[data-testid="template-select"]`);
     |                    ^ Error: page.click: Target page, context or browser has been closed
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