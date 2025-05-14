import { defineConfig } from '@playwright/test';

// Register tsconfig paths
try {
  require('tsconfig-paths/register');
} catch (e) {
  console.warn('Warning: tsconfig-paths could not be registered, path aliases may not work correctly in tests');
}

export default defineConfig({
  testDir: 'e2e/playwright',
  testMatch: ['**/*.spec.ts'],
  reporter: [['list'], ['html']],
  timeout: 120_000, // Allow plenty of time for tests to run
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : 1, // Run tests one at a time for reliability
  fullyParallel: false,
  use: { 
    baseURL: 'http://localhost:3000',
    trace: 'retain-on-failure',
    // Give actions plenty of time to complete
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
