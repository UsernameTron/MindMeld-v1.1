'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { LoadingIndicator } from '../ui/molecules/LoadingIndicator';
import { useAuth } from '../../context/AuthContext';

export interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    // Skip if still loading auth state from context
    if (isLoading) {
      console.log('RequireAuth: Auth context still loading, waiting...');
      return;
    }

    console.log('RequireAuth: Auth state from context:', { isAuthenticated });
    
    if (!isAuthenticated) {
      // User is not authenticated, redirect to login with return URL
      console.log('RequireAuth: User not authenticated, redirecting to login');
      const returnPath = encodeURIComponent(router.asPath);
      router.push(`/login?returnTo=${returnPath}`);
    } else {
      // User is authenticated, allow access
      console.log('RequireAuth: User is authenticated, allowing access');
      setAuthChecked(true);
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading indicator if:
  // 1. Auth context is still loading, OR
  // 2. We've determined auth is valid but component is still initializing
  if (isLoading || !authChecked) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingIndicator size="lg" />
      </div>
    );
  }

  // Only render children when authentication is confirmed
  return <>{children}</>;
};