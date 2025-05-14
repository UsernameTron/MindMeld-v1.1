// src/__mocks__/services/authService.js
import { vi } from 'vitest';
console.debug('[MOCK] frontend/src/__mocks__/services/authService.js loaded');

// Default JWT token for testing
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0';

// Define a standard test user for consistency across tests
const TEST_USER = {
  id: '123',
  email: 'testuser@example.com',
  name: 'Test User',
  role: 'user',
};

// Create API client mock
export const apiClient = {
  get: vi.fn().mockImplementation(url => {
    if (url === '/auth/session') return Promise.resolve({ data: { valid: true } });
    if (url === '/auth/user') return Promise.resolve({ data: TEST_USER });
    return Promise.resolve({ data: {} });
  }),
  post: vi.fn().mockImplementation(url => {
    if (url === '/auth/login') {
      return Promise.resolve({ 
        data: { 
          token: TEST_TOKEN,
          refreshToken: 'test-refresh-token',
          user: TEST_USER
        } 
      });
    }
    return Promise.resolve({ data: {} });
  }),
  put: vi.fn().mockResolvedValue({ data: {} }),
  delete: vi.fn().mockResolvedValue({ data: {} }),
};

// Mock token storage (simulating in-memory storage)
let storedToken = null;
let storedUser = null;

// Helper to set token for tests
export function setToken(token) {
  storedToken = token;
  return token;
}

// Helper to get token for tests
export function getToken() {
  return storedToken;
}

// Create the authService mock that matches the implementation
export const authService = {
  // Enhanced login implementation that properly stores tokens and user object
  login: vi.fn().mockImplementation(async (username, password) => {
    console.log('[AuthService Mock] Login called with:', username);
    
    // Successful login case
    if (username === 'testuser@example.com' && password === 'password123') {
      const authResponse = {
        token: TEST_TOKEN,
        refreshToken: 'test-refresh-token',
        user: { 
          id: '123', 
          email: username, 
          name: 'Test User',
          role: 'user'
        }
      };
      
      // Store token and user in-memory
      storedToken = authResponse.token;
      storedUser = authResponse.user;
      
      // Store user in localStorage for persistence (matches real implementation)
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(authResponse.user));
      }
      
      return authResponse;
    }
    
    // Failed login - match the error message expected in tests
    throw new Error('Invalid username or password');
  }),
  
  logout: vi.fn().mockImplementation(() => {
    // Clear stored values on logout
    storedToken = null;
    storedUser = null;
    
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('user');
    }
    
    return Promise.resolve(undefined);
  }),
  
  refresh: vi.fn().mockImplementation(() => {
    // Refresh should return a new token
    if (storedToken) {
      storedToken = `${TEST_TOKEN}-refreshed-${Date.now()}`;
      return Promise.resolve({ token: storedToken });
    }
    return Promise.reject(new Error('No token to refresh'));
  }),
  
  validateSession: vi.fn().mockImplementation(() => {
    // Session is valid if we have a token
    return Promise.resolve(!!storedToken);
  }),
  
  isAuthenticated: vi.fn().mockImplementation(() => {
    // We're authenticated if we have a token
    return !!storedToken;
  }),
  
  // Expose apiClient
  apiClient,
};

// Patch login mock to always have .mockResolvedValueOnce and .mockRejectedValueOnce
// These are important for test cases that need to override the default behavior
Object.assign(authService.login, {
  mockResolvedValueOnce(val) {
    return authService.login.mockImplementationOnce(() => {
      // If there's a user in the response, store it
      if (val && val.user) {
        storedUser = val.user;
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('user', JSON.stringify(val.user));
        }
      }
      
      // If there's a token in the response, store it
      if (val && val.token) {
        storedToken = val.token;
      }
      
      return Promise.resolve(val);
    });
  },
  mockRejectedValueOnce(err) {
    return authService.login.mockImplementationOnce(() => Promise.reject(err));
  }
});

// Add additional helpers for testing
authService.getUser = vi.fn().mockImplementation(() => {
  // Return stored user if available
  if (storedUser) {
    return Promise.resolve(storedUser);
  }
  
  // Try to get from localStorage
  if (typeof localStorage !== 'undefined') {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return Promise.resolve(JSON.parse(userStr));
      } catch (e) {
        // Invalid JSON, so remove it
        localStorage.removeItem('user');
      }
    }
  }
  
  // Return default test user if nothing else is available
  return Promise.resolve(TEST_USER);
});

// Reset all auth service mocks
export function resetAuthServiceMocks() {
  // Clear stored values
  storedToken = null;
  storedUser = null;
  
  // Reset mock functions
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
      const response = { 
        token: TEST_TOKEN, 
        refreshToken: 'test-refresh-token',
        user: { id: '123', email: username, name: 'Test User', role: 'user' } 
      };
      
      // Store token and user
      storedToken = response.token;
      storedUser = response.user;
      
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      
      return response;
    }
    throw new Error('Invalid username or password');
  });
  
  authService.isAuthenticated.mockImplementation(() => !!storedToken);
  authService.validateSession.mockImplementation(() => Promise.resolve(!!storedToken));
  authService.getUser.mockImplementation(() => Promise.resolve(storedUser || TEST_USER));
  
  // Reset apiClient default implementations
  apiClient.get.mockImplementation(url => {
    if (url === '/auth/session') return Promise.resolve({ data: { valid: !!storedToken } });
    if (url === '/auth/user') return Promise.resolve({ data: storedUser || TEST_USER });
    return Promise.resolve({ data: {} });
  });
  
  apiClient.post.mockImplementation(url => {
    if (url === '/auth/login') {
      return Promise.resolve({ 
        data: { 
          token: TEST_TOKEN,
          refreshToken: 'test-refresh-token',
          user: TEST_USER
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