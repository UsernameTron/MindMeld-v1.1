import { vi } from 'vitest';
// Mocks must be defined before imports
vi.mock('next/router');
vi.mock('next/navigation');
vi.mock('@/services/authService');

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginPage } from '../components/LoginPage';
// Import directly from mock files using alias paths
import { authService } from '@/__mocks__/services/authService';
import { RouterWrapper, routerFunctions } from '@test-utils/router';

console.debug('[TEST] authService import:', authService);
console.debug('[TEST] authService.login:', authService?.login);
console.debug('[TEST] typeof authService.login:', typeof authService?.login);

beforeEach(() => {
  vi.clearAllMocks();
  document.cookie = ''; // Clear cookies instead of localStorage
  console.debug('[TEST] beforeEach: authService:', authService);
  console.debug('[TEST] beforeEach: authService.login:', authService?.login);
  console.debug('[TEST] beforeEach: typeof authService.login:', typeof authService?.login);
});

describe('LoginPage', () => {
  test('submits form with credentials and redirects on success', async () => {
    (authService.login as any).mockResolvedValueOnce({
      token: 'test-token',
      refreshToken: 'refresh-token',
      user: { id: '123', email: 'testuser@example.com', name: 'Test User', role: 'user' },
    });
    render(
      <RouterWrapper>
        <LoginPage />
      </RouterWrapper>
    );
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('testuser@example.com', 'password123');
    });
    await waitFor(() => {
      expect(routerFunctions.replace).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('displays error message when login fails', async () => {
    (authService.login as any).mockRejectedValueOnce(new Error('Invalid username or password'));
    render(
      <RouterWrapper>
        <LoginPage />
      </RouterWrapper>
    );
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    const alert = await screen.findByRole('alert');
    expect(alert?.textContent?.toLowerCase()).toMatch(/invalid/);
  });
});