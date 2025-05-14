'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Set up token refresh interval (in minutes)
const REFRESH_INTERVAL = 15 * 60 * 1000; // 15 minutes

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Function to check and refresh auth status
  const checkAuthStatus = async () => {
    try {
      // Check if user is authenticated with the server
      const authStatus = await authService.isAuthenticated();
      setIsAuthenticated(authStatus);
      
      if (authStatus) {
        // If authenticated, fetch user profile
        const userProfile = await authService.getUserProfile();
        setUser(userProfile);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Set up token refresh on interval
  useEffect(() => {
    const refreshAuthToken = async () => {
      if (isAuthenticated) {
        try {
          await authService.refreshToken();
        } catch (error) {
          console.error('Token refresh failed:', error);
          // If refresh fails, log the user out
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    };

    // Check auth status on mount
    checkAuthStatus();

    // Set up periodic token refresh
    const intervalId = setInterval(refreshAuthToken, REFRESH_INTERVAL);
    
    // Clean up on unmount
    return () => clearInterval(intervalId);
  }, [isAuthenticated]);

  // Login function
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const userProfile = await authService.login(email, password);
      setUser(userProfile);
      setIsAuthenticated(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      login, 
      logout,
      isLoading
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};