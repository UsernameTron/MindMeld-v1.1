'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { LoadingIndicator } from '../ui/molecules/LoadingIndicator';
import { authService } from '../../services/authService';

export interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const isAuthenticated = authService.isAuthenticated();
        if (!isAuthenticated) {
          // Redirect to login with return URL
          router.push(`/login?returnTo=${encodeURIComponent(router.asPath)}`);
          return;
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Redirect on error
        router.push('/login');
      } finally {
        setIsChecking(false);
      }
    };
    checkAuth();
  }, [router]);

  if (isChecking) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingIndicator size="lg" />
      </div>
    );
  }

  return <>{children}</>;
};