'use client';
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../../services/authService';

interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isValidating, setIsValidating] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const validateAuth = async () => {
      setIsValidating(true);
      const valid = await authService.validateSession();
      setIsAuthenticated(valid);

      if (!valid) {
        // Redirect to login with return path
        navigate('/login', {
          state: { from: location.pathname },
        });
      }

      setIsValidating(false);
    };

    validateAuth();
  }, [navigate, location]);

  if (isValidating) {
    return null;
  }

  // Only render children if authenticated
  return isAuthenticated ? <>{children}</> : null;
};
