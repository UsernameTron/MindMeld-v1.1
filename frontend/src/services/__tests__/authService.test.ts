import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from '../authService';

describe('Auth Service', () => {
  beforeEach(() => {
    // Patch apiClient methods
    authService.apiClient.post = vi.fn();
    authService.apiClient.get = vi.fn();
  });

  describe('login', () => {
    it('should call /auth/login with credentials', async () => {
      (authService.apiClient.post as any).mockResolvedValueOnce({ data: { user: 'ok' } });
      await authService.login('test@example.com', 'password');
      expect(authService.apiClient.post).toHaveBeenCalledWith('/auth/login', { username: 'test@example.com', password: 'password' });
    });
    it('should throw error on failed login', async () => {
      (authService.apiClient.post as any).mockRejectedValueOnce(new Error('Invalid credentials'));
      await expect(authService.login('test@example.com', 'wrong')).rejects.toThrow();
    });
  });

  describe('logout', () => {
    it('should call /auth/logout', async () => {
      (authService.apiClient.post as any).mockResolvedValueOnce({});
      await authService.logout();
      expect(authService.apiClient.post).toHaveBeenCalledWith('/auth/logout');
    });
  });

  describe('validateSession', () => {
    it('should call /auth/session and return validity', async () => {
      (authService.apiClient.get as any).mockResolvedValueOnce({ data: { valid: true } });
      const result = await authService.validateSession();
      expect(authService.apiClient.get).toHaveBeenCalledWith('/auth/session');
      expect(result).toBe(true);
    });
  });

  describe('refresh', () => {
    it('should call /auth/refresh', async () => {
      (authService.apiClient.post as any).mockResolvedValueOnce({});
      await authService.refresh();
      expect(authService.apiClient.post).toHaveBeenCalledWith('/auth/refresh');
    });
  });

  describe('isAuthenticated', () => {
    it('should always return true (stub)', () => {
      expect(authService.isAuthenticated()).toBe(true);
    });
  });
});
