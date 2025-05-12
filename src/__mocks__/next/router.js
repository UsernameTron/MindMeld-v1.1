import { vi } from 'vitest';

export const push = vi.fn();
export const replace = vi.fn();
export const back = vi.fn();
export const prefetch = vi.fn();

export function useRouter() {
  return {
    push,
    replace,
    prefetch,
    back,
    pathname: '/current-path',
    query: {},
    asPath: '/current-path',
  };
}

export function resetRouterMocks() {
  push.mockReset();
  replace.mockReset();
  prefetch.mockReset();
  back.mockReset();
}
