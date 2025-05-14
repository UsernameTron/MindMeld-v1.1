// vitest.setup.ts - Consolidated Test Setup
// ==================================================
// This file serves as the central setup for all Vitest tests in the MindMeld application.
// It configures test utilities, mocks, and environment settings to ensure consistent behavior
// across all test files.
// ==================================================

// Polyfill ResizeObserver for jsdom+Recharts before any test code runs
if (typeof global !== 'undefined' && !global.ResizeObserver) {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
if (typeof window !== 'undefined' && !window.ResizeObserver) {
  window.ResizeObserver = global.ResizeObserver;
}

import './setupTests';

// --------------------------------------------------
// SECTION: Imports and Jest-DOM Matcher Setup
// --------------------------------------------------
import { expect, vi } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';
import '@testing-library/jest-dom';
import { configure } from '@testing-library/dom';

// Configure testing library and extend matchers
expect.extend(matchers);
configure({ 
  testIdAttribute: 'data-testid',
  // Add any additional RTL configuration here
});

// --------------------------------------------------
// SECTION: MSW (Mock Service Worker) Setup
// --------------------------------------------------
import { setupServer } from 'msw/node';
import { handlers } from './src/mocks/handlers';

// Setup MSW server with handlers
const server = setupServer(...handlers);

// MSW lifecycle hooks
beforeAll(() => {
  console.log('Test setup: Starting MSW server');
  server.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
  console.log('Test setup: Resetting MSW handlers');
  server.resetHandlers();
});

afterAll(() => {
  console.log('Test setup: Closing MSW server');
  server.close();
});

// --------------------------------------------------
// SECTION: Global/Browser API Mocks
// --------------------------------------------------

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock HTMLMediaElement for audio/video testing
Object.defineProperty(window, 'HTMLMediaElement', {
  writable: true,
  value: class MockHTMLMediaElement {
    constructor() {}
    play = vi.fn().mockImplementation(() => Promise.resolve());
    pause = vi.fn();
    canPlayType = vi.fn();
    load = vi.fn();
  }
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });

// Mock document.cookie
let cookieStore = '';
Object.defineProperty(document, 'cookie', {
  get: () => cookieStore,
  set: (val) => { cookieStore = val; },
  configurable: true,
});

// Mock window.location
const locationMock = {
  assign: vi.fn(),
  href: 'https://mindmeld-fresh-test.example.com',
  origin: 'https://mindmeld-fresh-test.example.com',
  pathname: '/',
  search: '',
  hash: '',
  reload: vi.fn(),
};
Object.defineProperty(window, 'location', {
  value: locationMock,
  writable: true,
});

// Mock global fetch
global.fetch = vi.fn();

// Mock indexedDB (for TTS service)
import indexedDBMock from './src/services/tts/__mocks__/indexedDBMock';
globalThis.indexedDB = indexedDBMock as any;

// --------------------------------------------------
// SECTION: Next.js and Service Mocks
// --------------------------------------------------

// Import reset functions from mocks
import { resetRouterMocks } from './src/__mocks__/next/router.js';
import { resetAuthServiceMocks } from './src/__mocks__/services/authService.js';
import { resetJwtMocks } from './src/__mocks__/utils/jwt.js';

// Mock Next.js components and functions
vi.mock('next/router', () => import('./src/__mocks__/next/router.js'));
vi.mock('next/navigation', () => import('./src/__mocks__/next/navigation.js'));

// Mock application services
vi.mock('@/services/authService', () => import('./src/__mocks__/services/authService.js'));
vi.mock('@/services/codeService', () => import('./src/__mocks__/services/codeService.js'));
vi.mock('@/services/api/apiClient', () => import('./src/__mocks__/services/api/apiClient.js'));
vi.mock('../src/services/authService', () => import('./src/__mocks__/services/authService.js'));
vi.mock('../../src/services/authService', () => import('./src/__mocks__/services/authService.js'));
vi.mock('src/services/authService', () => import('./src/__mocks__/services/authService.js'));

// Mock shims
vi.mock('@/shims/navigation', () => import('./src/__mocks__/shims/navigation'));

// --------------------------------------------------
// SECTION: Reset Logic Before Each Test
// --------------------------------------------------
beforeEach(() => {
  console.log('Test setup: Resetting mocks and state');
  
  // Reset all mocks
  vi.clearAllMocks();
  
  // Reset storage mocks
  localStorageMock.clear();
  sessionStorageMock.clear();
  cookieStore = '';
  
  // Reset specific mock implementations
  resetRouterMocks();
  resetAuthServiceMocks();
  resetJwtMocks();
  
  // Reset localStorage mock methods
  Object.values(localStorageMock).forEach(mockFn => {
    if (typeof mockFn === 'function' && mockFn.mockReset) {
      mockFn.mockReset();
    }
  });
});

// --------------------------------------------------
// SECTION: Custom Test Utilities
// --------------------------------------------------

// Add any custom test utilities here
// For example, helper functions for common test operations

// --------------------------------------------------
// SECTION: Jest-DOM Matcher Compatibility Notes
// --------------------------------------------------
// If you encounter issues with Jest-DOM matchers in Vitest, use the following replacements:
//   - toBeInTheDocument()   => expect(element).toBeTruthy()
//   - toHaveClass('foo')    => expect(element.classList.contains('foo')).toBe(true)
//   - toHaveAttribute('a')  => expect(element.hasAttribute('a')).toBe(true)
//   - toHaveTextContent('x')=> expect(element.textContent?.includes('x')).toBe(true)
// See scripts/fix-testing-matchers.js for more automated replacements.
// --------------------------------------------------