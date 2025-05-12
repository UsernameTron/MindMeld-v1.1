import { apiClient } from '../src/services/api/apiClient';

// Factory function for creating auth service instance
export function createAuthService() {
  return {
    /**
     * Authenticates user with username and password
     * @returns {Promise<{token: string, refreshToken: string}>}
     */
    async login(username, password) {
      const response = await apiClient.post('/auth/login', { username, password });
      this.saveTokens(response.data.token, response.data.refreshToken);
      return response.data;
    },

    /**
     * Validates current session token
     * @returns {Promise<boolean>}
     */
    async validateSession() {
      try {
        await apiClient.get('/auth/validate');
        return true;
      } catch (error) {
        return false;
      }
    },

    /**
     * Refreshes the authentication token
     * @returns {Promise<{token: string}>}
     */
    async refresh() {
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await apiClient.post('/auth/refresh', { refreshToken });
      localStorage.setItem('token', response.data.token);
      return response.data;
    },

    /**
     * Logs out the current user
     */
    async logout() {
      await apiClient.post('/auth/logout');
      this.clearTokens();
    },

    /**
     * Saves authentication tokens to localStorage
     */
    saveTokens(token, refreshToken) {
      localStorage.setItem('token', token);
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
    },

    /**
     * Clears authentication tokens
     */
    clearTokens() {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  };
}

// a singleton instance for convenience
export const authService = createAuthService();
