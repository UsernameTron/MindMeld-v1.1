import React, { useState } from 'react';
import { useRouter } from 'next/router'; // Using next/router, not next/navigation
import { apiClient } from '@/services/api/apiClient';
import { ErrorDisplay } from '@/components/ErrorDisplay';
import { LoadingIndicator } from '@/components/LoadingIndicator';
import { Card } from '@/components/ui/Card';
import { setAuthCookie } from '@/utils/setAuthCookie';
import type { LoginResponse } from '@/api/schema/generated/api-types';

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    // Get form data using FormData API
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    
    try {
      // Use the existing API client for login
      const response = await apiClient.request<LoginResponse>('/auth/token', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // Store the token and redirect
      setAuthCookie(response.access_token, response.expires_in);
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="max-w-md w-full p-6">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
        
        {error && (
          <ErrorDisplay 
            message={error}
            severity="error" 
            className="mb-4"
          />
        )}
        
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              name="email"
              placeholder="your@email.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              name="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <LoadingIndicator size="small" className="mr-2" /> 
                Logging in...
              </span>
            ) : (
              'Login'
            )}
          </button>
        </form>
      </Card>
    </div>
  );
}