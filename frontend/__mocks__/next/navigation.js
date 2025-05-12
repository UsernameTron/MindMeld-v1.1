import { vi } from 'vitest';

console.debug('[MOCK] frontend/__mocks__/next/navigation.js loaded');

// Router methods as mocks
const push = vi.fn((...args) => {
  console.debug('[MOCK] router.push called', ...args);
});
const replace = vi.fn((...args) => {
  console.debug('[MOCK] router.replace called', ...args);
});
const back = vi.fn((...args) => {
  console.debug('[MOCK] router.back called', ...args);
});
const prefetch = vi.fn((...args) => {
  console.debug('[MOCK] router.prefetch called', ...args);
});
const events = {
  on: vi.fn((...args) => console.debug('[MOCK] router.events.on', ...args)),
  off: vi.fn((...args) => console.debug('[MOCK] router.events.off', ...args)),
  emit: vi.fn((...args) => console.debug('[MOCK] router.events.emit', ...args)),
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
  console.debug('[MOCK] useRouter called');
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
