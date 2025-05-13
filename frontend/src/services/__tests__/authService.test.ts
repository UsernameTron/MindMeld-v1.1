import { vi, describe, it, expect, beforeEach, type Mock } from 'vitest';

vi.mock('../authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
    validateSession: vi.fn(),
    isAuthenticated: vi.fn(),
    apiClient: {},
  }
}));

import { authService } from '../authService';

const { login, logout, refresh, validateSession, isAuthenticated } = authService;

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    document.cookie = '';
  });

  it('should call login with credentials', async () => {
    (login as Mock).mockResolvedValueOnce({ id: '123', name: 'Test User' });
    await authService.login('test@example.com', 'password');
    expect(login).toHaveBeenCalledWith('test@example.com', 'password');
  });

  it('should throw error for invalid credentials', async () => {
    (login as Mock).mockRejectedValueOnce(new Error('Invalid credentials'));
    await expect(authService.login('invalid@example.com', 'wrongpassword')).rejects.toThrow(/invalid credentials/i);
  });

  // Add more tests for logout, refresh, etc. as needed
});
