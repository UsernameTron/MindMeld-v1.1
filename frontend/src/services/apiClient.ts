import axios from 'axios';
import { authService } from './authService';

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL!;
export const apiClient = axios.create({
  baseURL,
  withCredentials: true,
});

// Add response interceptor for handling token expiry
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Handle 401 responses (unauthorized)
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;
      // Try refreshing the token
      const refreshed = await authService.refresh();
      if (refreshed) {
        // Retry original request
        return apiClient(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);