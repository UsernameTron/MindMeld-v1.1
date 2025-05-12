import { expect } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

import { vi } from 'vitest';
import './src/test-setup';

// Centralize Next.js router/navigation mocks
vi.mock('next/router', () => import('./src/__mocks__/next/router.js'));
vi.mock('next/navigation', () => import('./src/__mocks__/next/navigation.js'));

// Mock auth and code services
vi.mock('@/services/authService', () => import('./src/__mocks__/services/authService.js'));
vi.mock('@/services/codeService', () => import('./src/__mocks__/services/codeService.js'));
vi.mock('@/services/api/apiClient', () => import('./src/__mocks__/services/api/apiClient.js'));

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

// Mock localStorage
class LocalStorageMock {
  store: Record<string, string> = {};

  clear() {
    this.store = {};
  }

  getItem(key: string) {
    return this.store[key] || null;
  }

  setItem(key: string, value: string) {
    this.store[key] = String(value);
  }

  removeItem(key: string) {
    delete this.store[key];
  }
}

Object.defineProperty(window, 'localStorage', {
  value: new LocalStorageMock(),
});

// Mock document.cookie
let cookieStore = '';
Object.defineProperty(document, 'cookie', {
  get: () => cookieStore,
  set: (val) => { cookieStore = val; },
  configurable: true,
});

// Reset all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
  window.localStorage.clear();
  cookieStore = '';
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
