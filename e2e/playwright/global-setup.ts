import { chromium } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * This runs once before all tests
 */
async function globalSetup() {
  // You can perform global setup tasks here
  console.log('Starting global setup for E2E tests...');

  // Pre-start the browser to save time during tests
  const browser = await chromium.launch();
  await browser.close();

  console.log('Global setup complete');
}

export default globalSetup;
