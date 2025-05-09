import { apiClient } from './api/apiClient';
import jwtDecode from 'jwt-decode';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface TokenPayload {
  sub: string;
  exp: number;
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      const response = await apiClient.post<AuthResponse>(
        '/auth/token',
        new URLSearchParams({
          username: credentials.username,
          password: credentials.password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const { access_token } = response.data;
      localStorage.setItem('auth_token', access_token);
      return true;
    } catch (error) {
      console.error('Login failed', error);
      return false;
    }
  },

  logout: (): void => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  },

  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;

    try {
      const decoded = jwtDecode<TokenPayload>(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp > currentTime;
    } catch (error) {
      return false;
    }
  },
};
