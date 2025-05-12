// src/test-utils/setupTests.js
import React from 'react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { resetRouterMocks } from '../src/__mocks__/next/router.js';
import { resetAuthServiceMocks } from '../src/__mocks__/services/authService.js';
import { resetJwtMocks } from '../src/__mocks__/utils/jwt.js';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: '',
});

// Reset all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
  document.cookie = '';
  localStorage.clear();
  resetRouterMocks();
  resetAuthServiceMocks();
  resetJwtMocks();
  Object.values(localStorageMock).forEach(mockFn => mockFn.mockReset());
});