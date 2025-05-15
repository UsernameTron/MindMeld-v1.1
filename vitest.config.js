import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const dirname = typeof __dirname !== 'undefined' 
  ? __dirname 
  : path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    // Exclude E2E Playwright tests and only include frontend unit tests
    include: ['frontend/**/*.{test,spec}.{ts,tsx}', './test-template-integration.spec.ts'],
    exclude: [
      '**/e2e/**', 
      '**/node_modules/**', 
      '**/playwright/**',
      '**/dist/**'
    ],
    setupFiles: ['./frontend/vitest.setup.ts'],
    alias: {
      // Base path aliases
      '@': path.resolve(dirname, './frontend/src'),
      '@components': path.resolve(dirname, './frontend/src/components'),
      '@services': path.resolve(dirname, './frontend/src/services'),
      '@utils': path.resolve(dirname, './frontend/src/utils'),
      '@context': path.resolve(dirname, './frontend/src/context'),
      '@shims': path.resolve(dirname, './frontend/src/shims'),
      
      // Relative path mappings for component imports
      './ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
      '../ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
      './LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
      '../LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
      '../../utils/cn': path.resolve(dirname, './frontend/src/utils/cn'),
      '../AnalysisResult/AnalysisResult': path.resolve(dirname, './frontend/src/components/ui/organisms/AnalysisResult/AnalysisResult'),
      '../CodeEditor/CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor'),
      './CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor'),
      
      // Mock the services
      'next/router': path.resolve(dirname, './frontend/src/__mocks__/next/router.js'),
      'next/navigation': path.resolve(dirname, './frontend/src/__mocks__/next/navigation.js'),
      '@/services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
      '@/services/codeService': path.resolve(dirname, './frontend/src/__mocks__/services/codeService.js'),
      '@/services/api/apiClient': path.resolve(dirname, './frontend/src/__mocks__/services/api/apiClient.js'),
      '../services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
      '../../services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
      '../../../services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
      'services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
      './authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js')
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(dirname, './frontend/src'),
      '@components': path.resolve(dirname, './frontend/src/components'),
      '@services': path.resolve(dirname, './frontend/src/services'),
      '@utils': path.resolve(dirname, './frontend/src/utils'),
      '@context': path.resolve(dirname, './frontend/src/context'),
      '@shims': path.resolve(dirname, './frontend/src/shims'),
      '@test-utils': path.resolve(dirname, './frontend/test-utils')
    }
  }
});
