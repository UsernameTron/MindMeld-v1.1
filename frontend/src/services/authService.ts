import { apiClient } from './apiClient';

export const authService = {
  async login(email: string, password: string): Promise<boolean> {
    try {
      await apiClient.post('/auth/token', { email, password });
      return true;
    } catch (error) {
      console.error('Login failed', error);
      return false;
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed', error);
    }
  },

  async refresh(): Promise<boolean> {
    try {
      await apiClient.post('/auth/refresh');
      return true;
    } catch (error) {
      console.error('Token refresh failed', error);
      return false;
    }
  },

  async validateSession(): Promise<boolean> {
    try {
      await apiClient.get('/auth/validate');
      return true;
    } catch (error: any) {
      if (error.response?.status === 401) {
        const refreshed = await this.refresh();
        if (!refreshed) {
          window.location.href = '/login';
          return false;
        }
        return true;
      }
      return false;
    }
  }
};
