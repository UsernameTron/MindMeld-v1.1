import { defineConfig } from '@playwright/test';

// Register tsconfig paths
try {
  require('tsconfig-paths/register');
} catch (e) {
  console.warn('Warning: tsconfig-paths could not be registered, path aliases may not work correctly in tests');
}

export default defineConfig({
  testDir: 'e2e/playwright',
  timeout: 120_000, // Allow plenty of time for tests to run
  retries: 1,
  workers: 1, // Run tests one at a time for reliability
  fullyParallel: false,
  use: { 
    baseURL: 'http://localhost:3000',
    // Give actions plenty of time to complete
    actionTimeout: 30000,
    navigationTimeout: 60000,
    // Slow down for visibility
    launchOptions: {
      slowMo: 100
    },
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
