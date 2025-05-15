// Playwright end-to-end workflow tests for MindMeld templates
// Covers the full flow: selection -> parameter input -> prompt generation

import { test, expect } from '@playwright/test';

const templates = [
  'deepResearch',
  'advancedReasoning',
  'counterfactual',
  'satiricalVoice',
  'pentagramVisual',
];

test.describe('MindMeld template end-to-end workflow', () => {
  for (const template of templates) {
    test(`complete workflow for ${template}`, async ({ page }) => {
      await page.goto('/');
      await page.click(`[data-testid="template-select"]`);
      await page.click(`[data-testid="template-option-${template}"]`);
      await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
      await page.fill(`[data-testid="template-form-${template}"] input`, 'test input');
      await page.click(`[data-testid="generate-prompt-btn"]`);
      await expect(page.locator(`[data-testid="prompt-display"]`)).toBeVisible();
      await expect(page.locator(`[data-testid="prompt-display"]`)).toContainText('test input');
    });
  }
});
