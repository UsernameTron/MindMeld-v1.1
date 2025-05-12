// src/__mocks__/next/router.js
import { vi } from 'vitest';

// Create mockable functions
export const push = vi.fn();
export const replace = vi.fn();
export const back = vi.fn();
export const prefetch = vi.fn();

// Export router hook
export function useRouter() {
  return {
    push,
    replace,
    prefetch,
    back,
    pathname: '/current-path',
    query: {},
    asPath: '/current-path',
    route: '/current-path',
    events: {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn()
    }
  };
}

// Default export for compatibility with some import styles
const defaultRouter = {
  push,
  replace,
  prefetch,
  back,
  pathname: '/current-path',
  query: {},
  asPath: '/current-path',
  route: '/current-path',
  events: {
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  }
};
export default defaultRouter;

// Reset all router mocks
export function resetRouterMocks() {
  push.mockReset();
  replace.mockReset();
  prefetch.mockReset();
  back.mockReset();
}