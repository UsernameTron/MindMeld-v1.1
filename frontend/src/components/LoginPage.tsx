import React, { useState } from 'react';
import { useRouter } from '@/shims/navigation';
import Card from '../components/ui/Card';
import { LoginForm } from './LoginForm';
import { authService } from '../services/authService';

export const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await authService.login(username, password);
      router.replace('/dashboard');
    } catch (err) {
      setError('Invalid username or password');
      console.error('Login failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <Card className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">Sign In</h1>
          <p className="text-gray-600">Enter your credentials to access your account</p>
        </div>
        <LoginForm
          onSubmit={handleLogin}
          isLoading={isLoading}
          error={error}
        />
      </Card>
    </div>
  );
};
