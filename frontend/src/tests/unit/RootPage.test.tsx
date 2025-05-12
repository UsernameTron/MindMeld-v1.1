// src/tests/unit/RootPage.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react';
// Must be before imports
vi.mock('next/router');
vi.mock('../../../src/services/authService');
vi.mock('../../../src/utils/jwt');

import RootPage from '../../../src/app/page';
import { mockAuthenticatedUser, mockUnauthenticatedUser } from '../../../test-utils/auth-test-utils';

// Helper to get the mocked push function from the __mocks__
const getMockedPush = () => {
  // @ts-ignore
  return require('next/router').push;
};

describe('RootPage', () => {
  beforeEach(() => {
    // Manually clear the push mock
    const push = getMockedPush();
    if (push && push.mockClear) push.mockClear();
  });

  test('redirects to dashboard when user is authenticated', async () => {
    mockAuthenticatedUser();
    render(<RootPage />);
    const push = getMockedPush();
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('redirects to login when user is not authenticated', async () => {
    mockUnauthenticatedUser();
    render(<RootPage />);
    const push = getMockedPush();
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith('/login');
    });
  });
});
