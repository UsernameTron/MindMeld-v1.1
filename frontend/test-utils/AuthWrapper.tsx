import React from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { AuthProvider } from '../src/context/AuthContext';
import { authService, setToken } from '../src/__mocks__/services/authService';

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
 */
export function createAuthWrapper(options: AuthWrapperOptions = defaultAuthOptions) {
  const mergedOptions = { ...defaultAuthOptions, ...options };
  
  // Set up mock auth state according to options
  if (mergedOptions.authenticated) {
    // Set mock token for auth state
    setToken('mock-test-token-' + Date.now());
    
    // Mock localStorage with user data
    if (typeof localStorage !== 'undefined' && mergedOptions.user) {
      localStorage.setItem('user', JSON.stringify(mergedOptions.user));
    }
    
    // Mock auth methods to return authenticated values
    authService.isAuthenticated.mockReturnValue(true);
    authService.validateSession.mockResolvedValue(true);
    authService.getUser.mockResolvedValue(mergedOptions.user);
  } else {
    // Mock unauthenticated state
    setToken(null);
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('user');
    }
    authService.isAuthenticated.mockReturnValue(false);
    authService.validateSession.mockResolvedValue(false);
    authService.getUser.mockResolvedValue(null);
  }
  
  // Skip initial auth check to avoid unnecessary API calls in tests
  if (!mergedOptions.withInitialAuthCheck) {
    jest.spyOn(React, 'useEffect').mockImplementationOnce(() => {});
  }
  
  // Return the auth wrapper component
  return function AuthWrapper({ children }: { children: React.ReactNode }) {
    return <AuthProvider>{children}</AuthProvider>;
  };
}

/**
 * Custom render function that wraps components with AuthProvider
 * for testing components that depend on auth state
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
 * A utility to simulate a login for testing authentication flows
 */
export async function mockSuccessfulLogin() {
  setToken('test-token-' + Date.now());
  localStorage.setItem('user', JSON.stringify(TEST_USER));
  authService.isAuthenticated.mockReturnValue(true);
  return Promise.resolve(TEST_USER);
}

/**
 * A utility to simulate a logout for testing authentication flows
 */
export async function mockLogout() {
  setToken(null);
  localStorage.removeItem('user');
  authService.isAuthenticated.mockReturnValue(false);
  return Promise.resolve();
}