import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.js'],
    globals: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
      'next/router': path.resolve(__dirname, 'src/__mocks__/next/router.js'),
      'next/navigation': path.resolve(__dirname, 'src/__mocks__/next/navigation.js'),
      '@/shims/navigation': path.resolve(__dirname, 'src/__mocks__/shims/navigation.ts'),
      '../services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      '@/services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
      'src/services/authService': path.resolve(__dirname, 'src/__mocks__/services/authService.js'),
    },
    deps: {
      inline: [/^next\/.*/],
    },
    coverage: {
      reporter: ['text', 'html'],
    },
  },
});
