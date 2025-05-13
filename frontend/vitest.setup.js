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

// Polyfill browser APIs for Vitest
const indexedDBMock = require('./src/services/tts/__mocks__/indexedDBMock');
global.indexedDB = indexedDBMock;
global.IDBKeyRange = {
  only: v => v,
  bound: (l, u) => [l, u],
  lowerBound: l => l,
  upperBound: u => u
};
global.URL = {
  createObjectURL: vi.fn(() => 'blob:mock-url')
};

class AudioMock {
  constructor() {
    this.src = '';
    this._listeners = {};
    this.paused = true;
  }
  play() {
    this.paused = false;
    if (this._listeners['play']) this._listeners['play'].forEach(fn => fn());
    return Promise.resolve();
  }
  pause() {
    this.paused = true;
    if (this._listeners['pause']) this._listeners['pause'].forEach(fn => fn());
  }
  addEventListener(event, fn) {
    if (!this._listeners[event]) this._listeners[event] = [];
    this._listeners[event].push(fn);
  }
  removeEventListener(event, fn) {
    if (this._listeners[event]) this._listeners[event] = this._listeners[event].filter(f => f !== fn);
  }
}
global.Audio = AudioMock;

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  document.cookie = '';
  routerMock.push.mockReset();
  routerMock.replace.mockReset();
  routerMock.back.mockReset();
  routerMock.prefetch.mockReset();
});
