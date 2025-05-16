import React from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { AuthProvider } from '../src/context/AuthContext';
import { authService, setToken } from '../src/__mocks__/services/authService';
import { ReactQueryProvider } from '../src/lib/reactQueryProvider';
import { vi } from 'vitest';

/**
 * Test User object to use in tests
 */
export const TEST_USER = {
  id: '123',
  email: 'testuser@example.com',
  name: 'Test User',
  role: 'user',
};

/**
 * Auth wrapper options for customizing the auth state in tests
 */
interface AuthWrapperOptions {
  authenticated?: boolean;
  user?: typeof TEST_USER;
  withInitialAuthCheck?: boolean;
}

/**
 * The default auth wrapper options
 */
const defaultAuthOptions: AuthWrapperOptions = {
  authenticated: true,
  user: TEST_USER,
  withInitialAuthCheck: true,
};

/**
 * Creates a wrapper for components that need auth context in tests
 * @param options AuthWrapperOptions
 * @returns React.FC wrapper
 */
export function createAuthWrapper(options: AuthWrapperOptions = defaultAuthOptions) {
  const mergedOptions = { ...defaultAuthOptions, ...options };

  // Set up mock auth state according to options
  if (mergedOptions.authenticated) {
    setToken('mock-test-token-' + Date.now());
    if (typeof window !== 'undefined' && mergedOptions.user) {
      window.localStorage.setItem('user', JSON.stringify(mergedOptions.user));
    }
    if (authService.isAuthenticated?.mockReturnValue) {
      authService.isAuthenticated.mockReturnValue(true);
    }
    if (authService.validateSession?.mockResolvedValue) {
      authService.validateSession.mockResolvedValue(true);
    }
    if (authService.getUserProfile?.mockResolvedValue) {
      authService.getUserProfile.mockResolvedValue(mergedOptions.user);
    }
  } else {
    setToken(null);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('user');
    }
    if (authService.isAuthenticated?.mockReturnValue) {
      authService.isAuthenticated.mockReturnValue(false);
    }
    if (authService.validateSession?.mockResolvedValue) {
      authService.validateSession.mockResolvedValue(false);
    }
    if (authService.getUserProfile?.mockResolvedValue) {
      authService.getUserProfile.mockResolvedValue(null);
    }
  }

  // Skip initial auth check to avoid unnecessary API calls in tests
  if (!mergedOptions.withInitialAuthCheck) {
    vi.spyOn(React, 'useEffect').mockImplementationOnce(() => {});
  }

  // Return the auth wrapper component
  return function AuthWrapper({ children }: { children: React.ReactNode }) {
    return <AuthProvider>{children}</AuthProvider>;
  };
}

/**
 * Custom render function that wraps components with AuthProvider
 * for testing components that depend on auth state
 * @param ui React element to render
 * @param authOptions AuthWrapperOptions
 * @param renderOptions RenderOptions
 * @returns RenderResult
 */
export function renderWithAuth(
  ui: React.ReactElement,
  authOptions: AuthWrapperOptions = defaultAuthOptions,
  renderOptions: Omit<RenderOptions, 'wrapper'> = {}
): RenderResult {
  const AuthWrapper = createAuthWrapper(authOptions);
  return render(ui, {
    wrapper: AuthWrapper,
    ...renderOptions,
  });
}

/**
 * Utility to wrap a component with both AuthProvider and QueryClientProvider
 * Use for components that use react-query hooks.
 * @param ui React element to render
 * @param authOptions AuthWrapperOptions
 * @param renderOptions RenderOptions
 * @returns RenderResult
 */
export function renderWithAuthAndQuery(
  ui: React.ReactElement,
  authOptions: AuthWrapperOptions = defaultAuthOptions,
  renderOptions: Omit<RenderOptions, 'wrapper'> = {}
): RenderResult {
  const AuthWrapper = createAuthWrapper(authOptions);
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <ReactQueryProvider>
      <AuthWrapper>{children}</AuthWrapper>
    </ReactQueryProvider>
  );
  return render(ui, {
    wrapper: Wrapper,
    ...renderOptions,
  });
}

/**
 * Simulate a login for testing authentication flows
 * @returns Promise<typeof TEST_USER>
 */
export async function mockSuccessfulLogin() {
  setToken('test-token-' + Date.now());
  if (typeof window !== 'undefined') {
    window.localStorage.setItem('user', JSON.stringify(TEST_USER));
  }
  if (authService.isAuthenticated?.mockReturnValue) {
    authService.isAuthenticated.mockReturnValue(true);
  }
  return Promise.resolve(TEST_USER);
}

/**
 * Simulate a logout for testing authentication flows
 * @returns Promise<void>
 */
export async function mockLogout() {
  setToken(null);
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem('user');
  }
  if (authService.isAuthenticated?.mockReturnValue) {
    authService.isAuthenticated.mockReturnValue(false);
  }
  return Promise.resolve();
}