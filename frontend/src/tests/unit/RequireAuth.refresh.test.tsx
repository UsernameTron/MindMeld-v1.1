// src/tests/unit/RequireAuth.refresh.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
// Must be before imports
vi.mock('next/router');
// Use aliased import for authService mock
vi.mock('@/services/authService');
vi.mock('../../../src/utils/jwt');

import { RequireAuth } from '../../../src/components/auth/RequireAuth';
// Update the import path below to the correct relative path if needed
// Correct import for test-utils/auth-test-utils (from src/tests/unit/ to frontend/test-utils/)
import { mockExpiredToken, mockTokenRefresh } from '../../../test-utils/auth-test-utils';
import { authService } from '@/services/authService';

describe('RequireAuth Token Refresh', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Ensure refreshToken is a mock function that resolves
    // @ts-ignore
    authService.refreshToken = vi.fn().mockResolvedValue('new-valid-token');
  });

  test('automatically refreshes expired token without redirecting', async () => {
    // Setup expired token that needs refresh
    mockExpiredToken('old-expired-token');
    // Mock successful token refresh
    // No need to call mockTokenRefresh if refreshToken is mocked above, but keep for clarity
    mockTokenRefresh('new-valid-token');

    render(
      <RequireAuth>
        <div>Protected Content</div>
      </RequireAuth>
    );

    // Verify refresh token was called
    await waitFor(() => {
      // @ts-ignore
      expect(authService.refreshToken).toHaveBeenCalled();
    });

    // Content should be visible after token refresh
    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });
});
