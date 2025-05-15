# Test info

- Name: MindMeld template end-to-end workflow >> complete workflow for advancedReasoning
- Location: /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-e2e.spec.ts:16:9

# Error details

```
TimeoutError: page.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid="template-select"]')

    at /Users/cpconnor/projects/mindmeld-fresh/e2e/playwright/tests/ui/template-e2e.spec.ts:18:18
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
   1 | // Playwright end-to-end workflow tests for MindMeld templates
   2 | // Covers the full flow: selection -> parameter input -> prompt generation
   3 |
   4 | import { test, expect } from '@playwright/test';
   5 |
   6 | const templates = [
   7 |   'deepResearch',
   8 |   'advancedReasoning',
   9 |   'counterfactual',
  10 |   'satiricalVoice',
  11 |   'pentagramVisual',
  12 | ];
  13 |
  14 | test.describe('MindMeld template end-to-end workflow', () => {
  15 |   for (const template of templates) {
  16 |     test(`complete workflow for ${template}`, async ({ page }) => {
  17 |       await page.goto('/');
> 18 |       await page.click(`[data-testid="template-select"]`);
     |                  ^ TimeoutError: page.click: Timeout 30000ms exceeded.
  19 |       await page.click(`[data-testid="template-option-${template}"]`);
  20 |       await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
  21 |       await page.fill(`[data-testid="template-form-${template}"] input`, 'test input');
  22 |       await page.click(`[data-testid="generate-prompt-btn"]`);
  23 |       await expect(page.locator(`[data-testid="prompt-display"]`)).toBeVisible();
  24 |       await expect(page.locator(`[data-testid="prompt-display"]`)).toContainText('test input');
  25 |     });
  26 |   }
  27 | });
  28 |
```