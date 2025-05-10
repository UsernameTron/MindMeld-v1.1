import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e/playwright',
  timeout: 60 * 1000,
  retries: process.env.CI ? 2 : 0,
  testMatch: ['*.spec.ts'],
  testIgnore: ['**/frontend/**/*.test.ts', '**/tests/**/*.test.ts'],
  use: {
    baseURL: 'http://localhost:3001',
    headless: true,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
  },
  webServer: {
    command: 'npm --prefix frontend run dev -- -p 3001',
    url: 'http://localhost:3001',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
