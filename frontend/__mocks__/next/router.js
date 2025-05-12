import { vi } from 'vitest';

// Router methods as mocks
const push = vi.fn();
const replace = vi.fn();
const back = vi.fn();
const prefetch = vi.fn();
const events = {
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn()
};

// Stable router object
const routerInstance = {
  push,
  replace,
  back,
  prefetch,
  pathname: '/current-path',
  query: {},
  asPath: '/current-path',
  route: '/current-path',
  events
};

// The useRouter function returns our stable instance
function useRouter() {
  return routerInstance;
}

// Expose the router methods directly as well
export { 
  push, 
  replace, 
  back, 
  prefetch, 
  events,
  useRouter
};

// Default export for ESM compatibility
export default {
  useRouter,
  push,
  replace,
  back,
  prefetch,
  events
};
