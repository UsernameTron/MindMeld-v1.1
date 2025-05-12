// Must be before imports
vi.mock('next/router');
vi.mock('../../src/utils/jwt');
// Use aliased import for authService mock
vi.mock('@/services/authService');

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { RequireAuth } from '../../src/components/auth/RequireAuth';
import { mockAuthenticatedUser, mockUnauthenticatedUser, mockTokenValidation } from '../test-utils/auth-test-utils';
import { authService } from '@/services/authService';

// Helper to get the mocked push function from the __mocks__
const getMockedPush = () => {
  // @ts-ignore
  return require('next/router').push;
};

describe('RequireAuth', () => {
  let push: any;
  beforeEach(() => {
    // Remove all mocks manually for compatibility
    // @ts-ignore
    push = require('next/router').push;
    if (!push || typeof push !== 'function' || !('mockClear' in push)) {
      // @ts-ignore
      require('next/router').push = vi.fn();
      push = require('next/router').push;
    }
    if (push && push.mockClear) push.mockClear();
    document.cookie = '';

    // Patch authService.login to be a vi.fn() if not already
    if (typeof authService.login !== 'function' || !('mockResolvedValueOnce' in authService.login)) {
      // @ts-ignore
      authService.login = vi.fn(authService.login);
    }
  });

  test('redirects to /login when not authenticated', async () => {
    mockUnauthenticatedUser();
    mockTokenValidation(false);
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Secret</div>
        </RequireAuth>
      </MemoryRouter>
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith('/login'));
  });

  test('renders children when authenticated', async () => {
    mockAuthenticatedUser();
    mockTokenValidation(true);
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Secret</div>
        </RequireAuth>
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText('Secret')).toBeInTheDocument());
    const push = getMockedPush();
    expect(push).not.toHaveBeenCalled();
  });

  test('redirects to /login on validation error', async () => {
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Secret</div>
        </RequireAuth>
      </MemoryRouter>
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith('/login'));
  });

  test('redirects to login when user is not authenticated', async () => {
    // Set up unauthenticated state
    mockUnauthenticatedUser();
    
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Protected Content</div>
        </RequireAuth>
      </MemoryRouter>
    );
    
    // Verify redirect happens
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith('/login');
    });
    
    // Content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('renders children when user is authenticated', async () => {
    // Set up authenticated state
    mockAuthenticatedUser();
    mockTokenValidation(true);
    
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Protected Content</div>
        </RequireAuth>
      </MemoryRouter>
    );
    
    // Verify children are rendered
    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
    
    // No redirect should happen
    expect(push).not.toHaveBeenCalled();
  });

  // Patch authService.refresh to be a vi.fn() for refresh test
  test('attempts to refresh token when expired', async () => {
    document.cookie = 'auth_token=expired-token';
    mockTokenValidation(false);
    // Patch refresh to a vi.fn()
    // @ts-ignore
    authService.refresh = vi.fn().mockResolvedValue(true);
    render(
      <MemoryRouter initialEntries={["/protected"]}>
        <RequireAuth>
          <div>Protected Content</div>
        </RequireAuth>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(authService.refresh).toHaveBeenCalled();
    });
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});