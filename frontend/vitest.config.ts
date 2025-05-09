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
      reporter: ['text', 'lcov', 'html'],
      include: [
        'src/components/Button.tsx',
        'src/components/atoms/Card.tsx',
        'src/components/molecules/ErrorDisplay.tsx', 
        'src/components/molecules/LoadingIndicator.tsx',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
        perFile: true
      }
    },
    include: [
      'src/**/*.test.{ts,tsx}'
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
