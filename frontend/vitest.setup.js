import { vi } from 'vitest';
import routerMock from './__mocks__/next/router.js';
// Ensure NODE_ENV is set to 'test' for our shims to work correctly
process.env.NODE_ENV = 'test';
console.debug('[SETUP] vitest.setup.js loaded');
console.debug('[SETUP] routerMock:', routerMock);
console.debug('[SETUP] NODE_ENV:', process.env.NODE_ENV);

vi.mock('next/router', () => ({
  ...routerMock,
  default: routerMock,
}));

vi.mock('next/navigation', () => ({
  ...routerMock,
  default: routerMock,
}));

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  document.cookie = '';
  routerMock.push.mockReset();
  routerMock.replace.mockReset();
  routerMock.back.mockReset();
  routerMock.prefetch.mockReset();
});
