import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      },
      exclude: [
        'node_modules/**',
        '.next/**',
        'public/**',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        'src/types/**'
      ]
    },
    include: [
      'src/**/*.test.{ts,tsx}',
      'tests/**/*.test.{ts,tsx}'
    ],
    exclude: [
      '**/node_modules/**',
      '**/.next/**',
      '**/dist/**',
    ],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  optimizeDeps: {
    include: [
      '@testing-library/react',
      '@testing-library/jest-dom',
      'vitest',
      'tsconfig-paths'
    ]
  }
});
