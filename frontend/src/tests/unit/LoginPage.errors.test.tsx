// src/tests/unit/LoginPage.errors.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// Must be before imports
vi.mock('next/router');
// Use aliased import for authService mock
vi.mock('@/services/authService');

// Fix import path for LoginPage to use relative import
import LoginPage from '../../../pages/login';
import { authService } from '@/services/authService';

describe('LoginPage Error Handling', () => {
  beforeEach(() => {
    // Manually clear mocks for authService.login
    // @ts-ignore
    if (authService.login && authService.login.mockClear) authService.login.mockClear();
  });

  test('displays appropriate error message for invalid credentials', async () => {
    // Mock auth service to reject with specific error
    // @ts-ignore
    authService.login.mockRejectedValueOnce(new Error('Invalid email or password'));
    const user = userEvent.setup();
    render(<LoginPage />);
    // Fill and submit form
    await user.type(screen.getByLabelText(/email/i), 'wrong@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
    await user.click(screen.getByRole('button', { name: /login/i }));
    // Verify error message appears
    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
    // Verify loading state is removed
    expect(screen.queryByText(/logging in/i)).not.toBeInTheDocument();
  });

  test('displays network error message when server is unreachable', async () => {
    // Mock network failure
    // @ts-ignore
    authService.login.mockRejectedValueOnce(new Error('Network Error'));
    const user = userEvent.setup();
    render(<LoginPage />);
    // Fill and submit form
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));
    // Verify appropriate error message appears
    await waitFor(() => {
      expect(screen.getByText(/unable to connect/i)).toBeInTheDocument();
    });
  });
});
