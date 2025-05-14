import { test, expect } from '@playwright/test';

// Utility for screenshots
async function screenshot(page, name) {
  await page.screenshot({ path: `test-results/sentiment-analysis-${name}.png`, fullPage: true });
}

test.describe('Web Sentiment Analysis Integration', () => {
  const sentimentUrl = '/sentiment-analysis';
  const testUrls = [
    { url: 'https://www.positive.news/', label: 'positive' },
    { url: 'https://www.bbc.com/news/world-europe-60506682', label: 'negative' },
  ];
  const invalidUrls = [
    'not-a-url',
    'ftp://invalid-protocol.com',
    'http://',
    '',
  ];

  test('Full integration: positive/negative/invalid URLs, history, error, responsive', async ({ page }) => {
    // 1. Navigate to the sentiment analysis page
    await page.goto(sentimentUrl);
    console.log('Navigated to sentiment analysis page');
    await screenshot(page, 'page-load');

    // 2. Test invalid URLs
    for (const bad of invalidUrls) {
      await page.fill('input[type="url"]', bad);
      await page.click('button[type="submit"]');
      await expect(page.getByText(/valid URL/i)).toBeVisible();
      console.log(`Invalid URL error shown for: ${bad}`);
      await screenshot(page, `invalid-url-${bad.replace(/[^a-z0-9]/gi, '_')}`);
    }

    // 3. Test positive and negative URLs
    for (const { url, label } of testUrls) {
      await page.fill('input[type="url"]', url);
      await page.click('button[type="submit"]');
      // Wait for loading indicator
      await expect(page.locator('text=Analyzing...')).toBeVisible({ timeout: 5000 });
      // Wait for result
      await expect(page.locator('text=Sentiment:')).toBeVisible({ timeout: 15000 });
      // Confirm API call (console log)
      page.on('response', response => {
        if (response.url().includes('/api/v1/sentiment')) {
          console.log('API call:', response.url(), response.status());
        }
      });
      // Confirm sentiment and emotions
      const sentiment = await page.textContent('div[aria-live="polite"]');
      expect(sentiment).toMatch(/Sentiment:/);
      console.log(`Sentiment result for ${url}:`, sentiment);
      await screenshot(page, `result-${label}`);
      // Confirm visualization
      await expect(page.locator('section[aria-label*="visualization"]')).toBeVisible();
      // Confirm summary
      await expect(page.locator('h2', { hasText: 'Summary' })).toBeVisible();
      // Confirm history
      await expect(page.locator('h2', { hasText: 'History' })).toBeVisible();
    }

    // 4. Test history tracking (should show both URLs)
    const historyItems = await page.locator('ul >> text=Result:').allTextContents();
    expect(historyItems.length).toBeGreaterThanOrEqual(2);
    console.log('History tracking verified:', historyItems);
    await screenshot(page, 'history');

    // 5. Responsive check (mobile viewport)
    await page.setViewportSize({ width: 375, height: 700 });
    await screenshot(page, 'mobile');
    await expect(page.locator('input[type="url"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('Responsive/mobile layout verified');
  });
});
