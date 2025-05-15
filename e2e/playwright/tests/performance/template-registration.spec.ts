// Playwright performance test for simultaneous template registrations
// Measures time to register multiple templates in parallel

import { test, expect } from '@playwright/test';

test('performance: simultaneous template registrations', async ({ page }) => {
  await page.goto('/');
  const templateIds = [
    'deepResearch',
    'advancedReasoning',
    'counterfactual',
    'satiricalVoice',
    'pentagramVisual',
  ];
  const start = Date.now();
  await Promise.all(
    templateIds.map(async (template) => {
      await page.click(`[data-testid="template-select"]`);
      await page.click(`[data-testid="template-option-${template}"]`);
      await expect(page.locator(`[data-testid="template-form-${template}"]`)).toBeVisible();
    })
  );
  const duration = Date.now() - start;
  // Save result for CI reporting
  console.log(`Performance: Registered all templates in ${duration}ms`);
  expect(duration).toBeLessThan(3000); // Example threshold
});
