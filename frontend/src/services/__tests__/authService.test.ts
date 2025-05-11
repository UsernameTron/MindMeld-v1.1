import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createAuthService } from '../authService';

// Mock apiClient
const apiClient = {
  post: vi.fn(),
  get: vi.fn(),
};

// Mock local storage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

let authService: ReturnType<typeof createAuthService>;

describe('Auth Service', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    apiClient.post.mockReset();
    apiClient.get.mockReset();
    mockLocalStorage.setItem.mockClear();
    authService = createAuthService(apiClient);
  });

  describe('login', () => {
    it('should store token in localStorage on successful login', async () => {
      const mockToken = 'mock-jwt-token';
      apiClient.post.mockResolvedValueOnce({
        data: { access_token: mockToken },
      });

      await authService.login('test@example.com', 'password');

      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/token', {
        username: 'test@example.com',
        password: 'password',
      });
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', mockToken);
    });

    it('should throw error on failed login', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Invalid credentials'));
      mockLocalStorage.setItem.mockClear();
      await expect(authService.login('test@example.com', 'wrong')).rejects.toThrow();
      expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
    });
  });

  describe('logout', () => {
    it('should remove token from localStorage', async () => {
      mockLocalStorage.setItem('token', 'existing-token');
      
      apiClient.post.mockResolvedValueOnce({});
      
      await authService.logout();

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      const mockToken = 'stored-token';
      mockLocalStorage.setItem('token', mockToken);

      const token = authService.getToken();

      expect(token).toBe(mockToken);
    });

    it('should return null if no token exists', () => {
      const token = authService.getToken();

      expect(token).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      mockLocalStorage.setItem('token', 'valid-token');

      const result = authService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when token does not exist', () => {
      const result = authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('token refresh', () => {
    it('should update token on successful refresh', async () => {
      const originalToken = 'original-token';
      const refreshedToken = 'refreshed-token';
      mockLocalStorage.setItem('token', originalToken);
      apiClient.post.mockResolvedValueOnce({
        data: { access_token: refreshedToken },
      });
      const result = await authService.refresh();
      expect(result).toBe(true);
      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh');
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', refreshedToken);
    });

    it('should return false on failed refresh', async () => {
      const originalToken = 'original-token';
      mockLocalStorage.setItem('token', originalToken);
      apiClient.post.mockRejectedValueOnce(new Error('Refresh failed'));
      const result = await authService.refresh();
      expect(result).toBe(false);
      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh');
    });
    
    it('should attempt refresh on 401 from validateSession', async () => {
      mockLocalStorage.setItem('token', 'expired-token');
      apiClient.get.mockRejectedValueOnce({ response: { status: 401 } });
      apiClient.post.mockResolvedValueOnce({ data: { access_token: 'new-token' } });
      const result = await authService.validateSession();
      expect(apiClient.get).toHaveBeenCalledWith('/auth/validate');
      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh');
      expect(result).toBe(true);
      expect(mockLocalStorage.getItem('token')).toBe('new-token');
    });
  });
});
