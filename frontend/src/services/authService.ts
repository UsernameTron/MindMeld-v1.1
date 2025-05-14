import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

interface User {
  id: string;
  name: string;
  email: string;
}

interface LoginResponse {
  user: User;
  message: string;
}

interface RefreshResponse {
  accessToken: string;
}

// In memory token storage - NOT accessible to scripts on the page, only this module
let inMemoryToken: string | null = null;

const setToken = (token: string | null) => {
  inMemoryToken = token;
};

const getToken = (): string | null => {
  return inMemoryToken;
};

// Track if we're in the middle of refreshing to prevent multiple refreshes
let isRefreshing = false;
// Queue of callbacks to execute after token refresh
let subscribers: ((token: string) => void)[] = [];

// DO NOT use this function to set cookies directly
// Now we only use the server-side /api/auth/token endpoint for setting cookies
function mockAuthResponse(email: string, password: string): Promise<User> {
  if (email === "test@example.com" && password === "Test123!") {
    const user = { id: '1', name: 'Test User', email };
    // Store token in memory and localStorage (but NOT cookie)
    const mockToken = 'mock-jwt-token-' + Date.now();
    setToken(mockToken);
    // Store user data for UI
    localStorage.setItem('user', JSON.stringify(user));
    return Promise.resolve(user);
  }
  return Promise.reject(new Error('Invalid credentials'));
}

export const authService = {
  login: async (email: string, password: string): Promise<User> => {
    console.log('authService: Login attempt with email:', email);

    try {
      console.log('authService: Sending POST request to /api/auth/token');
      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include' // Important for HttpOnly cookies
      });
      
      console.log('authService: Response status:', response.status);
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Expected JSON, got: ${text.substring(0, 100)}`);
      }
      
      if (!response.ok) {
        const error = await response.json();
        console.error('authService: Login failed with server error:', error);
        throw new Error(error.message || 'Login failed');
      }
      
      const data: LoginResponse = await response.json();
      console.log('authService: Login response:', data);
      
      // Store user data in local storage for UI personalization
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      
      return data.user;
    } catch (error) {
      console.error('authService: Login error:', error);
      throw error;
    }
  },
  
  logout: async (): Promise<void> => {
    // Clear any in-memory token
    setToken(null);
    
    // Clear localStorage user data
    localStorage.removeItem('user');
    
    // Call the logout endpoint to clear server-side cookies
    try {
      await fetch('/api/auth/logout', { 
        method: 'POST',
        credentials: 'include' // Important for HttpOnly cookies
      });
    } catch (error) {
      console.error('authService: Logout error:', error);
      // Even if server logout fails, we've cleared client-side storage
    }
  },
  
  getUserProfile: async (): Promise<User> => {
    try {
      const response = await authService.fetchWithAuth('/api/auth/user');
      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }
      return await response.json();
    } catch (error) {
      console.error('Get user profile error:', error);
      throw error;
    }
  },
  
  isAuthenticated: async (): Promise<boolean> => {
    try {
      // Verify authentication with server
      console.log('authService: Validating auth with server');
      const response = await fetch('/api/auth/validate', {
        credentials: 'include' // Important for HttpOnly cookies
      });
      return response.ok;
    } catch (error) {
      console.error('authService: Auth validation error:', error);
      return false;
    }
  },

  refreshToken: async (): Promise<string> => {
    // If we're already refreshing, don't start another refresh
    if (isRefreshing) {
      return new Promise((resolve) => {
        subscribers.push(resolve);
      });
    }

    isRefreshing = true;
    
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include', // important for sending cookies
      });
      
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      
      const data: RefreshResponse = await response.json();
      const accessToken = data.accessToken;
      
      // Store the token in memory, not localStorage
      setToken(accessToken);
      
      // Notify all subscribers that refresh is complete
      subscribers.forEach(callback => callback(accessToken));
      subscribers = [];
      
      return accessToken;
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    } finally {
      isRefreshing = false;
    }
  },

  fetchWithAuth: async (url: string, options: RequestInit = {}): Promise<Response> => {
    const token = getToken();
    
    // Initial request headers
    const headers = {
      ...options.headers,
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
    
    // Make initial request
    let response = await fetch(url, { 
      ...options, 
      headers,
      credentials: 'include' // Important for cookies
    });
    
    // If 401 Unauthorized, try to refresh token and retry
    if (response.status === 401) {
      try {
        const newToken = await authService.refreshToken();
        
        // Retry with new token
        const newHeaders = {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        };
        
        return fetch(url, { 
          ...options, 
          headers: newHeaders,
          credentials: 'include'
        });
      } catch (error) {
        // If refresh fails, propagate the 401
        return response;
      }
    }
    
    return response;
  }
};