import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

interface User {
  id: string;
  name: string;
  email: string;
}

interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export const authService = {
  login: async (email: string, password: string): Promise<User> => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Login failed');
      }
      
      const data: LoginResponse = await response.json();
      
      // Store access token in memory
      sessionStorage.setItem('accessToken', data.accessToken);
      
      // Store user data
      localStorage.setItem('user', JSON.stringify(data.user));
      
      return data.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  logout: async (): Promise<void> => {
    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    await fetch('/api/auth/logout', { method: 'POST' });
  },
  
  getCurrentUser: (): User | null => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },
  
  isAuthenticated: (): boolean => {
    return !!sessionStorage.getItem('accessToken');
  },

  refreshToken: async (): Promise<string> => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include', // important for sending cookies
      });
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      const data = await response.json();
      const accessToken = data.accessToken;
      sessionStorage.setItem('accessToken', accessToken);
      return accessToken;
    } catch (error) {
      console.error('Refresh token error:', error);
      // Force logout on refresh failure
      sessionStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      throw error;
    }
  },

  fetchWithAuth: async (url: string, options: RequestInit = {}): Promise<Response> => {
    // Add auth header to options
    const token = sessionStorage.getItem('accessToken');
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
    // Make initial request
    let response = await fetch(url, { ...options, headers });
    // If 401 Unauthorized, try to refresh token and retry
    if (response.status === 401) {
      try {
        await authService.refreshToken();
        // Retry with new token
        const newToken = sessionStorage.getItem('accessToken');
        const newHeaders = {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        };
        return fetch(url, { ...options, headers: newHeaders });
      } catch (error) {
        // If refresh fails, propagate the 401
        return response;
      }
    }
    return response;
  }
};