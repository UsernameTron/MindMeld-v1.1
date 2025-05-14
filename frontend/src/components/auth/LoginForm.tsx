import React, { useState, FormEvent } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../../context/AuthContext';

// Default test credentials for debugging
const TEST_CREDENTIALS = {
  email: "test@example.com",
  password: "Test123!"
};

interface LoginFormProps {
  redirectPath?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({ 
  redirectPath = '/dashboard'
}) => {
  const router = useRouter();
  const [email, setEmail] = useState(TEST_CREDENTIALS.email);
  const [password, setPassword] = useState(TEST_CREDENTIALS.password);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loginStatus, setLoginStatus] = useState<string | null>(null);
  
  const { login } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log('LoginForm: Login form submitted with email:', email);
    setIsLoading(true);
    setError(null);
    setLoginStatus('Attempting login...');
    
    try {
      console.log('LoginForm: Calling auth context login function');
      await login(email, password);
      console.log('LoginForm: Login successful, redirecting to:', redirectPath);
      setLoginStatus('Login successful! Redirecting...');
      
      // Short delay to show success message before redirect
      setTimeout(() => {
        router.push(redirectPath);
      }, 500);
    } catch (err) {
      console.error('LoginForm: Login failed:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
      setLoginStatus(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}
      
      {loginStatus && !error && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
          <div className="text-sm text-green-700">{loginStatus}</div>
        </div>
      )}
      
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email address
        </label>
        <div className="mt-1">
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <div className="mt-1">
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </button>
      </div>
      
      <div className="text-center text-xs text-gray-500">
        (Test credentials are pre-filled)
      </div>
    </form>
  );
};