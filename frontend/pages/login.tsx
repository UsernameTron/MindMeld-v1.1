import React, { useState } from 'react';
import { useRouter } from '../src/shims/router';
// Use the factory pattern instead of direct import
import { createAuthService } from '../src/services/authService';
import { apiClient } from '@/services/api/apiClient';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  // Create authService instance
  const authService = createAuthService();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    console.log('[Login] Attempting login with:', email);
    
    try {
      console.log('[Login] Calling authService.login...');
      const result = await authService.login(email, password);
      console.log('[Login] Login result:', result);
      
      if (result) {
        console.log('[Login] Login successful, redirecting to dashboard');
        // Use window.location.href instead of router.push for a hard navigation
        // This ensures a full page reload with new cookies applied
        window.location.href = '/dashboard';
      } else {
        console.log('[Login] Login unsuccessful');
        setError('Invalid email or password');
      }
    } catch (error: unknown) {
      console.error('[Login] Login error:', error);
      setError(error instanceof Error ? error.message : 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div role="alert" className="bg-red-100 text-red-700 p-3 rounded">
              {error}
            </div>
          )}
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="your@email.com"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <button 
            type="submit" 
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
