import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { authService } from '../src/services/authService';
import { LoginForm } from '../src/components/auth/LoginForm';

// Fallback Card component if custom one is not available
const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-white shadow rounded-lg ${className || ''}`}>{children}</div>
);

export default function LoginPage() {
  const router = useRouter();
  const { returnTo } = router.query;
  const redirectPath = typeof returnTo === 'string' ? returnTo : '/dashboard';
  
  // Only redirect if already logged in
  useEffect(() => {
    console.log('LoginPage: Checking auth state');
    const checkAuth = async () => {
      try {
        const isAuth = await authService.isAuthenticated();
        console.log('LoginPage: Authentication check result:', isAuth);
        if (isAuth) {
          console.log('LoginPage: Already authenticated, redirecting to:', redirectPath);
          router.push(redirectPath);
        }
      } catch (err) {
        console.error('LoginPage: Error checking auth state:', err);
      }
    };
    checkAuth();
  }, [router, redirectPath]);
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          MindMeld Login
        </h1>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your credentials to access the platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="py-8 px-4 sm:px-10">
          <LoginForm redirectPath={redirectPath} />
        </Card>
      </div>
    </div>
  );
}
