// src/__mocks__/services/authService.js
import { vi } from 'vitest';
console.debug('[MOCK] frontend/src/__mocks__/services/authService.js loaded');

// Default JWT token for testing
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0';

export const authService = {
  login: vi.fn().mockImplementation(async (email, password) => {
    console.log('[AuthService Mock] Login called with:', email);
    
    // Successful login case
    if (email === 'testuser@example.com' && password === 'password123') {
      const token = TEST_TOKEN;
      localStorage.setItem('token', token);
      
      return {
        token,
        user: { 
          id: '123', 
          email, 
          name: 'Test User',
          role: 'user'
        }
      };
    }
    
    // Failed login - match the error message expected in tests
    throw new Error('Invalid username or password');
  }),
  
  logout: vi.fn().mockResolvedValue(undefined),
  
  refreshToken: vi.fn().mockImplementation(async () => {
    const newToken = 'new-valid-token';
    localStorage.setItem('token', newToken);
    return newToken;
  }),
  
  isAuthenticated: vi.fn().mockReturnValue(true),
  
  validateSession: vi.fn().mockResolvedValue(true)
};

// Patch login mock to always have .mockResolvedValueOnce and .mockRejectedValueOnce
Object.assign(authService.login, {
  mockResolvedValueOnce(val) {
    return authService.login.mockImplementationOnce(() => Promise.resolve(val));
  },
  mockRejectedValueOnce(err) {
    return authService.login.mockImplementationOnce(() => Promise.reject(err));
  }
});

// Add missing methods and nested mocks for full test compatibility
// Add apiClient mock if referenced in tests
export const apiClient = {
  get: vi.fn().mockImplementation(url => {
    if (url === '/auth/validate') return Promise.resolve({ data: { valid: true } });
    return Promise.resolve({ data: {} });
  }),
  post: vi.fn().mockResolvedValue({ data: {} }),
  put: vi.fn(),
  delete: vi.fn(),
};

authService.apiClient = apiClient;

authService.getUser = vi.fn().mockResolvedValue({
  id: '123',
  email: 'testuser@example.com',
  name: 'Test User',
  role: 'user',
});

// Reset all auth service mocks
export function resetAuthServiceMocks() {
  Object.values(authService).forEach(mockFn => {
    if (typeof mockFn === 'function' && mockFn.mockReset) {
      mockFn.mockReset();
    }
  });
  
  // Reset api client mocks
  if (authService.apiClient) {
    Object.values(authService.apiClient).forEach(mock => {
      if (typeof mock === 'function' && mock.mockReset) mock.mockReset();
    });
  }
  
  // Reset default implementations
  authService.login.mockImplementation(async (email, password) => {
    if (email === 'testuser@example.com' && password === 'password123') {
      const token = TEST_TOKEN;
      localStorage.setItem('token', token);
      return { token, user: { id: '123', email, name: 'Test User' } };
    }
    throw new Error('Invalid username or password');
  });
  
  authService.isAuthenticated.mockReturnValue(true);
  authService.validateSession.mockResolvedValue(true);
}

console.debug('[MOCK] frontend/src/__mocks__/services/authService.js exports:', {authService});
export { authService };
export default authService;