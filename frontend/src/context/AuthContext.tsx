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
      console.log('AuthContext: Checking authentication status');
      
      // First try to load user from localStorage (for immediately showing UI)
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
          // Don't set isAuthenticated=true yet until we verify with server
        } catch (e) {
          console.error('AuthContext: Failed to parse stored user data');
          localStorage.removeItem('user'); // Remove invalid data
        }
      }
      
      // Verify authentication with server
      const authStatus = await authService.isAuthenticated();
      console.log('AuthContext: Auth status from server:', authStatus);
      setIsAuthenticated(authStatus);
      
      if (authStatus) {
        // If authenticated, fetch current user profile
        try {
          const userProfile = await authService.getUserProfile();
          setUser(userProfile);
          // Update stored user data if needed
          localStorage.setItem('user', JSON.stringify(userProfile));
        } catch (profileError) {
          console.error('AuthContext: Failed to fetch user profile:', profileError);
          // Fall back to stored user if available
          if (!user && storedUser) {
            try {
              setUser(JSON.parse(storedUser));
            } catch (e) {
              console.error('AuthContext: Failed to parse stored user data');
            }
          }
        }
      } else {
        // Clear user if not authenticated
        setUser(null);
        localStorage.removeItem('user');
      }
    } catch (error) {
      console.error('AuthContext: Error checking auth status:', error);
      // If server check fails, assume not authenticated
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Set up initial auth check and refresh timer
  useEffect(() => {
    console.log('AuthContext: Initial auth check');
    checkAuthStatus();

    // Set up a periodic refresh
    const intervalId = setInterval(() => {
      console.log('AuthContext: Refreshing auth status');
      checkAuthStatus();
    }, REFRESH_INTERVAL);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  // Login function
  const login = async (email: string, password: string): Promise<void> => {
    console.log('AuthContext: Login attempt with email:', email);
    setIsLoading(true);
    try {
      const user = await authService.login(email, password);
      setUser(user);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(user));
      console.log('AuthContext: Login successful for:', user.email);
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('user');
      throw error; // Re-throw to be handled by the login component
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    console.log('AuthContext: Logout attempt');
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('user');
      console.log('AuthContext: Logout successful');
    } catch (error) {
      console.error('AuthContext: Logout error:', error);
      // Even if server-side logout fails, clear local state
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('user');
      // No need to re-throw here as we're clearing auth state regardless
    } finally {
      setIsLoading(false);
    }
  };

  // Expose the auth context value
  const contextValue = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};