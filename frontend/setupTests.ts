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
