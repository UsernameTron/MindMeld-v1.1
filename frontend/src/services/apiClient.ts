import axios from 'axios';
// import type { components } from '@/api/schema';
// TODO: The '@/api/schema' import is missing. If you have an OpenAPI-generated types file, update the path. Otherwise, comment this out or provide a fallback type.
// export type LoginRequest = components['schemas']['LoginRequest'];
// export type LoginResponse = components['schemas']['LoginResponse'];

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL!;
export const apiClient = axios.create({
  baseURL,
  withCredentials: true,
});

// export async function loginUser(credentials: LoginRequest): Promise<LoginResponse> {
//   const res = await apiClient.post<LoginResponse>('/login', credentials);
//   return res.data;
// }

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
