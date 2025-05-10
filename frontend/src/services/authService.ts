export function createAuthService(apiClient: any) {
  return {
    async login(email: string, password: string): Promise<boolean> {
      try {
        const response = await apiClient.post('/auth/token', { 
          username: email, 
          password: password 
        });
        if (response && response.data && response.data.access_token) {
          window.localStorage.setItem('token', response.data.access_token);
        }
        return true;
      } catch (error) {
        console.error('Login failed', error);
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
