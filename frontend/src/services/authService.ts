import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// Mock authentication service for frontend-only testing
export function createAuthService() {
  // Remove all localStorage usage
  // Tokens are now managed by HttpOnly cookies (server-side)

  const apiClient: AxiosInstance = axios.create({
    baseURL: '/api',
    withCredentials: true, // Always send cookies
  });

  // 401 → refresh → retry interceptor
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
      if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          await apiClient.post('/auth/refresh');
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Optionally: redirect to login
          return Promise.reject(refreshError);
        }
      }
      return Promise.reject(error);
    }
  );

  return {
    async login(username: string, password: string) {
      // Example: call real API, rely on HttpOnly cookie
      const res = await apiClient.post('/auth/login', { username, password });
      return res.data;
    },
    async validateSession() {
      // Example: call real API
      const res = await apiClient.get('/auth/session');
      return res.data.valid;
    },
    async refresh() {
      await apiClient.post('/auth/refresh');
      return true;
    },
    async logout() {
      await apiClient.post('/auth/logout');
    },
    isAuthenticated() {
      // Optionally: check session
      return true; // Or implement a real check
    },
    apiClient, // Export for testability
  };
}

// Export a singleton instance for convenience
export const authService = createAuthService();