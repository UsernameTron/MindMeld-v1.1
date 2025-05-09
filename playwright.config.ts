import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e', // Only run tests from the e2e/ folder
  timeout: 30_000,
  use: {
    baseURL: 'http://localhost:3001',
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  // No webServer or test globs
});
