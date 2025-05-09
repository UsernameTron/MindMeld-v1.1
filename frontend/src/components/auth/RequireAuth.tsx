import React from 'react';
import { authService } from '../../services/authService';

interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  if (typeof window !== 'undefined' && !authService.isAuthenticated()) {
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    return null;
  }
  return <>{children}</>;
};
