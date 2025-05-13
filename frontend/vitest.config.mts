import { defineConfig } from 'vitest/config';
import path from 'path';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: 'jsdom',
    globals: true,
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      'tests/ci/**',
      'e2e/**', // Exclude all E2E tests
      'frontend/e2e/**', // Exclude Playwright E2E tests
      'tests/**',
      '**/*.e2e.{js,ts,jsx,tsx}', // Exclude any e2e test files
      '**/*.playwright.{js,ts,jsx,tsx}' // Exclude any Playwright test files
    ],
    include: [
      '**/*.{test,spec}.{js,ts,jsx,tsx}',
      'frontend/**/*.{test,spec}.{js,ts,jsx,tsx}'
    ],
    setupFiles: [path.resolve(__dirname, './vitest.setup.js')],
    deps: {
      inline: [/@testing-library\/react/, /@testing-library\/jest-dom/, /@headlessui\/react/]
    },
  },
  resolve: {
    alias: {
      // --- MOCKS FIRST (for test overrides) ---
      '@/__mocks__/services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      '@/__mocks__/services/codeService': path.resolve(__dirname, 'src/__mocks__/services/codeService.js'),
      '@/__mocks__/services/api/apiClient': path.resolve(__dirname, 'src/__mocks__/services/api/apiClient.js'),
      '@/__mocks__/shims/navigation': path.resolve(__dirname, 'src/__mocks__/shims/navigation.ts'),
      '@/__mocks__/next/router': path.resolve(__dirname, 'src/__mocks__/next/router.js'),
      '@/__mocks__/next/navigation': path.resolve(__dirname, 'src/__mocks__/next/navigation.js'),
      // Next.js router/navigation mocks
      'next/router': path.resolve(__dirname, 'src/__mocks__/next/router.js'),
      'next/navigation': path.resolve(__dirname, 'src/__mocks__/next/navigation.js'),
      // JWT mock
      '@/utils/jwt': path.resolve(__dirname, 'src/__mocks__/utils/jwt.js'),
      '../utils/jwt': path.resolve(__dirname, 'src/__mocks__/utils/jwt.js'),
      '../../utils/jwt': path.resolve(__dirname, 'src/__mocks__/utils/jwt.js'),
      // --- REAL IMPLEMENTATIONS ---
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@styles': path.resolve(__dirname, 'src/design/tokens'),
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
      '@/services/authService': path.resolve(__dirname, 'src/services/authService.ts'),
      '@/services/codeService': path.resolve(__dirname, 'src/services/codeService.ts'),
      '@/services/api/apiClient': path.resolve(__dirname, 'src/services/api/apiClient.ts'),
      '@/shims/navigation': path.resolve(__dirname, 'src/shims/navigation.ts'),
      // Legacy/relative aliases for compatibility
      'src/services/authService': path.resolve(__dirname, 'src/services/authService.ts'),
      'src/services/codeService': path.resolve(__dirname, 'src/services/codeService.ts'),
      'src/services/api/apiClient': path.resolve(__dirname, 'src/services/api/apiClient.ts'),
      'src/shims/navigation': path.resolve(__dirname, 'src/shims/navigation.ts'),
      '../services/authService': path.resolve(__dirname, 'src/services/authService.ts'),
      '../services/codeService': path.resolve(__dirname, 'src/services/codeService.ts'),
      '../services/api/apiClient': path.resolve(__dirname, 'src/services/api/apiClient.ts'),
      '../shims/navigation': path.resolve(__dirname, 'src/shims/navigation.ts'),
      '../../services/authService': path.resolve(__dirname, 'src/services/authService.ts'),
      '../../services/codeService': path.resolve(__dirname, 'src/services/codeService.ts'),
      '../../services/api/apiClient': path.resolve(__dirname, 'src/services/api/apiClient.ts'),
      '../../shims/navigation': path.resolve(__dirname, 'src/shims/navigation.ts')
    }
  }
});
