// src/__mocks__/services/authService.js
import { vi } from 'vitest';
console.debug('[MOCK] frontend/src/__mocks__/services/authService.js loaded');

// Default JWT token for testing
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0';

// Create API client mock
export const apiClient = {
  get: vi.fn().mockImplementation(url => {
    if (url === '/auth/session') return Promise.resolve({ data: { valid: true } });
    return Promise.resolve({ data: {} });
  }),
  post: vi.fn().mockImplementation(url => {
    if (url === '/auth/login') {
      return Promise.resolve({ 
        data: { 
          token: TEST_TOKEN,
          user: { 
            id: '123', 
            email: 'testuser@example.com', 
            name: 'Test User',
            role: 'user'
          }
        } 
      });
    }
    return Promise.resolve({ data: {} });
  }),
  put: vi.fn().mockResolvedValue({ data: {} }),
  delete: vi.fn().mockResolvedValue({ data: {} }),
};

// Create the authService mock that matches the implementation
export const authService = {
  login: vi.fn().mockImplementation(async (username, password) => {
    console.log('[AuthService Mock] Login called with:', username);
    
    // Successful login case
    if (username === 'testuser@example.com' && password === 'password123') {
      return {
        token: TEST_TOKEN,
        user: { 
          id: '123', 
          email: username, 
          name: 'Test User',
          role: 'user'
        }
      };
    }
    
    // Failed login - match the error message expected in tests
    throw new Error('Invalid username or password');
  }),
  
  logout: vi.fn().mockResolvedValue(undefined),
  
  refresh: vi.fn().mockResolvedValue(true),
  
  validateSession: vi.fn().mockResolvedValue(true),
  
  isAuthenticated: vi.fn().mockReturnValue(true),
  
  apiClient,
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

// Add additional helpers for testing
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
  Object.values(apiClient).forEach(mock => {
    if (typeof mock === 'function' && mock.mockReset) mock.mockReset();
  });
  
  // Reset default implementations
  authService.login.mockImplementation(async (username, password) => {
    if (username === 'testuser@example.com' && password === 'password123') {
      return { 
        token: TEST_TOKEN, 
        user: { id: '123', email: username, name: 'Test User', role: 'user' } 
      };
    }
    throw new Error('Invalid username or password');
  });
  
  authService.isAuthenticated.mockReturnValue(true);
  authService.validateSession.mockResolvedValue(true);
  
  // Reset apiClient default implementations
  apiClient.get.mockImplementation(url => {
    if (url === '/auth/session') return Promise.resolve({ data: { valid: true } });
    return Promise.resolve({ data: {} });
  });
  
  apiClient.post.mockImplementation(url => {
    if (url === '/auth/login') {
      return Promise.resolve({ 
        data: { 
          token: TEST_TOKEN,
          user: { id: '123', email: 'testuser@example.com', name: 'Test User', role: 'user' }
        } 
      });
    }
    return Promise.resolve({ data: {} });
  });
}

console.debug('[MOCK] frontend/src/__mocks__/services/authService.js exports:', {authService});

// Export a createAuthService function to match the real implementation
export function createAuthService() {
  return authService;
}

export default authService;