import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL!;
export const apiClient = axios.create({
  baseURL,
  withCredentials: true,
});

// NOTE: Interceptor logic for token refresh should be refactored to use DI if needed.

apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    // Handle 401 responses (unauthorized)
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;
      // Try refreshing the token
      // NOTE: Interceptor logic for token refresh should be refactored to use DI if needed.
    }
    return Promise.reject(error);
  }
);
