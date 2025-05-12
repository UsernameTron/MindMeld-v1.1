import { vi } from 'vitest';
import { authService } from '../src/services/authService';
import { isTokenExpired } from '../src/utils/jwt';
import { screen } from '@testing-library/react';

export function mockAuthenticatedUser() {
  document.cookie = 'auth_token=valid-token';
  // @ts-ignore
  isTokenExpired.mockReturnValue(false);
}

export function mockUnauthenticatedUser() {
  document.cookie = '';
}

export function mockExpiredToken(token = 'expired-token') {
  document.cookie = `auth_token=${token}`;
  // @ts-ignore
  isTokenExpired.mockReturnValue(true);
}

export function mockTokenRefresh(newToken = 'new-valid-token') {
  // @ts-ignore
  authService.refreshToken = vi.fn().mockResolvedValueOnce(newToken);
}

export function mockAuthError(error = 'Authentication failed') {
  // @ts-ignore
  authService.login = vi.fn().mockRejectedValueOnce(new Error(error));
}

export function mockNetworkError() {
  // @ts-ignore
  authService.login = vi.fn().mockRejectedValueOnce(new Error('Network Error'));
}

// Form test helpers
export async function fillLoginForm(user: any, email = 'test@example.com', password = 'password123') {
  await user.type(screen.getByLabelText(/email/i), email);
  await user.type(screen.getByLabelText(/password/i), password);
}

export async function submitLoginForm(user: any) {
  await user.click(screen.getByRole('button', { name: /login/i }));
}
