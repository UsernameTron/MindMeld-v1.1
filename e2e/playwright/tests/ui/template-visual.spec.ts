// Playwright UI visual regression and responsive tests for MindMeld templates
// This suite is separate from integration tests for maintainability

import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
];

const templates = [
  'deepResearch',
  'advancedReasoning',
  'counterfactual',
  'satiricalVoice',
  'pentagramVisual',
];

for (const viewport of viewports) {
  for (const template of templates) {
    test.describe(`${template} template UI (${viewport.name})`, () => {
      test.use({ viewport: { width: viewport.width, height: viewport.height } });

      test(`renders template selection for ${template}`, async ({ page }) => {
        await page.goto('/');
        await page.click(`[data-testid="template-select"]`);
        await page.click(`[data-testid="template-option-${template}"]`);
        await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
        await page.screenshot({ path: `screenshots/${template}-selection-${viewport.name}.png` });
      });

      test(`renders parameter form for ${template}`, async ({ page }) => {
        await page.goto('/');
        await page.click(`[data-testid="template-select"]`);
        await page.click(`[data-testid="template-option-${template}"]`);
        await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
        await page.screenshot({ path: `screenshots/${template}-form-${viewport.name}.png` });
      });

      test(`renders prompt display for ${template}`, async ({ page }) => {
        await page.goto('/');
        await page.click(`[data-testid="template-select"]`);
        await page.click(`[data-testid="template-option-${template}"]`);
        await page.fill(`[data-testid="template-form-${template}"] input`, 'test input');
        await page.click(`[data-testid="generate-prompt-btn"]`);
        await expect(page.locator(`[data-testid="prompt-display"]`)).toBeVisible();
        await page.screenshot({ path: `screenshots/${template}-prompt-${viewport.name}.png` });
      });
    });
  }
}
