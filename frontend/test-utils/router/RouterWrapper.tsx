import React from 'react';
import { vi } from 'vitest';

// Create mock router functions that can be accessed and asserted in tests
export const routerFunctions = {
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  prefetch: vi.fn(),
  refresh: vi.fn(),
};

/**
 * Wrapper component for Next.js router
 * Provides the necessary context for components that use router
 */
export const RouterWrapper: React.FC<{
  children: React.ReactNode;
  asPath?: string;
  pathname?: string;
  query?: Record<string, string>;
}> = ({ 
  children, 
  asPath = '/', 
  pathname = '/',
  query = {} 
}) => {
  // Mock routing context
  return (
    <div data-testid="router-wrapper">
      {children}
    </div>
  );
};

/**
 * Reset all router mock functions
 */
export const resetRouterMocks = () => {
  Object.values(routerFunctions).forEach(mockFn => {
    if (typeof mockFn === 'function' && mockFn.mockReset) {
      mockFn.mockReset();
    }
  });
};