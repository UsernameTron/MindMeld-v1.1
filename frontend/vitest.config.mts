import { defineConfig } from 'vitest/config';
import path from 'path';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: 'jsdom',
    include: [
      'src/**/*.test.{js,ts,jsx,tsx}',
      'tests/**/*.test.{js,ts,jsx,tsx}'
    ],
    setupFiles: [path.resolve(__dirname, './vitest.setup.ts')],
    globals: true,
    deps: {
      inline: [/@testing-library\/react/, /@testing-library\/jest-dom/]
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
