import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

import { storybookTest } from '@storybook/experimental-addon-test/vitest-plugin';

const dirname =
  typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// More info at: https://storybook.js.org/docs/writing-tests/test-addon
export default defineConfig({
  test: {
    environment: 'node',
    include: ['app/**/*.test.{js,ts,jsx,tsx}', 'tests/**/*.test.{js,ts,jsx,tsx}'],
    exclude: ['frontend/**', 'e2e/**', '**/*.spec.ts', 'node_modules/**'],
    setupFiles: ['./vitest.setup.ts'],
  },
  projects: [
    {
      name: 'backend',
      testMatch: ['**/app/**/*.test.{js,ts}', '**/tests/**/*.test.{js,ts}'],
      environment: 'node',
      exclude: ['**/e2e/**', '**/frontend/**', '**/scripts/**', '**/playwright/**', '**/*.spec.ts'],
    },
    {
      extends: true,
      plugins: [
        // The plugin will run tests for the stories defined in your Storybook config
        // See options at: https://storybook.js.org/docs/writing-tests/test-addon#storybooktest
        storybookTest({ configDir: path.join(dirname, '.storybook') }),
      ],
      test: {
        name: 'storybook',
        browser: {
          enabled: true,
          headless: true,
          name: 'chromium',
          provider: 'playwright'
        },
        setupFiles: ['.storybook/vitest.setup.js'],
      },
    },
  ],
});
