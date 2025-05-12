'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '../../services/authService';

const BYPASS_AUTH_CHECKS = false;

interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isValidating, setIsValidating] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const validateAuth = async () => {
      setIsValidating(true);
      console.debug('[RequireAuth] Starting session validation');
      try {
        const valid = await authService.validateSession();
        console.debug('[RequireAuth] Session valid:', valid);
        setIsAuthenticated(valid);
        if (!BYPASS_AUTH_CHECKS && !valid) {
          console.debug('[RequireAuth] Not authenticated, redirecting to /login');
          router.replace('/login');
        }
      } catch (error) {
        console.error('[RequireAuth] Session validation error:', error);
        setIsAuthenticated(false);
        if (!BYPASS_AUTH_CHECKS) {
          console.debug('[RequireAuth] Error state, redirecting to /login');
          router.replace('/login');
        }
      } finally {
        setIsValidating(false);
        console.debug('[RequireAuth] Validation complete');
      }
    };
    validateAuth();
  }, [router]);

  useEffect(() => {
    console.debug('[RequireAuth] Render state:', {
      isAuthenticated,
      isValidating,
    });
  }, [isAuthenticated, isValidating]);

  if (isValidating) {
    return null;
  }

  return (BYPASS_AUTH_CHECKS || isAuthenticated) ? <>{children}</> : null;
};