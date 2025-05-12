import { vi } from 'vitest';
import { authService } from '@/services/authService';
import { isTokenExpired } from '@/utils/jwt';

export function mockAuthenticatedUser(token = 'valid-token') {
  document.cookie = `auth_token=${token}`;
  localStorage.setItem('token', token);
  vi.mocked(isTokenExpired).mockReturnValue(false);
  vi.mocked(authService.isAuthenticated).mockReturnValue(true);
}

export function mockUnauthenticatedUser() {
  document.cookie = '';
  localStorage.removeItem('token');
  vi.mocked(isTokenExpired).mockReturnValue(true);
  vi.mocked(authService.isAuthenticated).mockReturnValue(false);
}
