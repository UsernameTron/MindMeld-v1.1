// src/__mocks__/next/navigation.js
import { vi } from 'vitest';

// Create mockable functions
export const push = vi.fn().mockResolvedValue(true);
export const replace = vi.fn().mockResolvedValue(true);
export const back = vi.fn();
export const prefetch = vi.fn().mockResolvedValue();
export const refresh = vi.fn();

// Export router hook that matches Next.js App Router
export function useRouter() {
  return {
    push,
    replace,
    back,
    prefetch,
    refresh,
    pathname: '/current-path',
    // App router doesn't have query
    asPath: '/current-path',
    route: '/current-path',
  };
}

// Default export for compatibility with some import styles
const defaultRouter = {
  push,
  replace,
  back,
  prefetch,
  refresh,
  pathname: '/current-path',
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
export function resetNavigationMocks() {
  push.mockReset();
  replace.mockReset();
  back.mockReset();
  prefetch.mockReset();
  refresh.mockReset();
}
