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
      'e2e/**',
      'tests/**'
    ],
    include: [
      '**/*.{test,spec}.{js,ts,jsx,tsx}',
      'frontend/**/*.{test,spec}.{js,ts,jsx,tsx}'
    ],
    setupFiles: [path.resolve(__dirname, './vitest.setup.ts')],
    deps: {
      inline: [/@testing-library\/react/, /@testing-library\/jest-dom/, /@headlessui\/react/]
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/src'),
      '@components': path.resolve(__dirname, 'frontend/src/components'),
      '@styles': path.resolve(__dirname, 'frontend/src/design/tokens'),
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
      'next/router': path.resolve(__dirname, '../__mocks__/next/router.js'),
      'next/navigation': path.resolve(__dirname, '../__mocks__/next/router.js'),
      './next/router': path.resolve(__dirname, '../__mocks__/next/router.js'),
      '../next/router': path.resolve(__dirname, '../__mocks__/next/router.js'),
      '../../next/router': path.resolve(__dirname, '../__mocks__/next/router.js'),
      './next/navigation': path.resolve(__dirname, '../__mocks__/next/router.js'),
      '../next/navigation': path.resolve(__dirname, '../__mocks__/next/router.js'),
      '../../next/navigation': path.resolve(__dirname, '../__mocks__/next/router.js'),
      '@/services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      '../services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      '../../services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      '@/utils/jwt': path.resolve(__dirname, '../src/__mocks__/utils/jwt.js'),
      'src/utils/jwt': path.resolve(__dirname, '../src/__mocks__/utils/jwt.js'),
      '../utils/jwt': path.resolve(__dirname, '../src/__mocks__/utils/jwt.js'),
      '../../utils/jwt': path.resolve(__dirname, '../src/__mocks__/utils/jwt.js')
    }
  }
});
