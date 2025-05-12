// Mock authentication service for frontend-only testing
export function createAuthService() {
  const saveTokens = (token: string, refreshToken: string) => {
    localStorage.setItem('token', token);
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken);
    }
  };

  const clearTokens = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  };

  const getToken = () => localStorage.getItem('token');

  return {
    /**
     * Mock implementation for authentication
     * In production, this would call the real API
     */
    async login(username: string, password: string) {
      console.log('[AuthService] Using mock login implementation');
      if (username === 'testuser@example.com' && password === 'password123') {
        const mockToken =
          'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0';
        const mockRefreshToken = 'mock-refresh-token-12345';
        saveTokens(mockToken, mockRefreshToken);
        return {
          token: mockToken,
          refreshToken: mockRefreshToken,
          user: {
            id: '123',
            email: username,
            name: 'Test User',
            passwordChangeRequired: false,
            isVerified: true,
            lastLogin: new Date().toISOString(),
            role: 'user',
          },
        };
      }
      console.error('[AuthService] Login failed - Invalid credentials');
      throw new Error('Invalid username or password');
    },

    async validateSession() {
      console.log('[AuthService] Using mock validateSession');
      const token = getToken();
      return !!token;
    },

    async refresh() {
      console.log('[AuthService] Using mock refresh');
      const mockToken =
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0.refreshed';
      localStorage.setItem('token', mockToken);
      return true;
    },

    async logout() {
      console.log('[AuthService] Using mock logout');
      clearTokens();
    },

    saveTokens,
    clearTokens,
    getToken,

    isAuthenticated() {
      return !!getToken();
    },
  };
}

// Export a singleton instance for convenience
export const authService = createAuthService();