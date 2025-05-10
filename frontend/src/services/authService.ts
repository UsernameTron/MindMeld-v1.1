import axios from 'axios';

export function createAuthService(apiClient: any) {
  return {
    async login(email: string, password: string): Promise<boolean> {
      try {
        console.log('[AuthService] Attempting login with:', email);
        const response = await apiClient.post('/api/auth/token', { 
          username: email, 
          password: password 
        });
        console.log('[AuthService] Login response:', response);
        if (response && response.data && response.data.access_token) {
          console.log('[AuthService] Setting token in localStorage and cookie');
          // Keep token in localStorage for client-side access
          window.localStorage.setItem('token', response.data.access_token);
          
          // Set auth_token cookie for server-side middleware
          document.cookie = `auth_token=${response.data.access_token}; path=/; max-age=3600; SameSite=Strict`;
          console.log('[AuthService] Cookie set', document.cookie);
          
          // Give the app a moment to process cookies and localStorage
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        return true;
      } catch (error) {
        console.error('[AuthService] Login failed', error);
        throw error;
      }
    },

    async logout(): Promise<void> {
      try {
        await apiClient.post('/auth/logout');
        window.localStorage.removeItem('token');
        window.location.assign('/login');
      } catch (error) {
        console.error('Logout failed', error);
        window.localStorage.removeItem('token');
      }
    },

    async refresh(): Promise<boolean> {
      try {
        const response = await apiClient.post('/auth/refresh');
        if (response && response.data && response.data.access_token) {
          window.localStorage.setItem('token', response.data.access_token);
        }
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
      } catch (error: unknown) {
        const errorWithResponse = error as { response?: { status?: number } };
        if (errorWithResponse.response?.status === 401) {
          const refreshed = await this.refresh();
          if (!refreshed) {
            window.location.assign('/login');
            return false;
          }
          return true;
        }
        return false;
      }
    },

    getToken(): string | null {
      return window.localStorage.getItem('token');
    },

    isAuthenticated(): boolean {
      return !!window.localStorage.getItem('token');
    },
  };
}

// Create a default instance with axios
export const authService = createAuthService(axios);
