import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from './services/authService';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  useEffect(() => {
    const validateSession = async () => {
      setIsLoading(true);
      console.debug('Validating session...');
      try {
        const isValid = await authService.validateSession();
        console.debug('Session valid:', isValid);
        setIsAuthenticated(isValid);
      } catch (error) {
        console.error('Session validation failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };
    validateSession();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      console.debug('Logging in user:', username);
      await authService.login(username, password);
      setIsAuthenticated(true);
      console.debug('Login successful, isAuthenticated:', true);
    } catch (error) {
      console.error('Login failed:', error);
      setIsAuthenticated(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      console.debug('Logging out user');
      await authService.logout();
      setIsAuthenticated(false);
      console.debug('Logout complete, isAuthenticated:', false);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    isAuthenticated,
    isLoading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
