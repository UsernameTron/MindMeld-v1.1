import React, { useEffect, useState } from 'react';
import { useRouter } from '@/shims/router';
import { fetchData } from '../src/services/dataService.js';
// Use the factory pattern instead of direct import
import { createAuthService } from '@/services/authService.js';
import { apiClient } from '@/services/api/apiClient.js';

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sessionValid, setSessionValid] = useState(true);
  // Create authService instance
  const authService = createAuthService(apiClient);

  const loadData = async () => {
    setLoading(true);
    try {
      // Validate session before fetching data
      const isValid = await authService.validateSession();
      if (!isValid) {
        setSessionValid(false);
        router.push('/login');
        return;
      }

      const result = await fetchData();
      console.log('[Dashboard] refreshed data=', result);
      setData(result.value);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('[Dashboard] fetching data…');
    
    // First check if session is valid
    authService.validateSession().then(isValid => {
      if (!isValid) {
        console.log('[Dashboard] Invalid session, redirecting to login');
        setSessionValid(false);
        router.push('/login');
        return;
      }
      
      // Then fetch data
      fetchData().then(d => {
        console.log('[Dashboard] data=', d);
        setData(d.value);
      }).catch(console.error);
    });
  }, [router]);

  // If session becomes invalid, don't render the dashboard
  if (!sessionValid) {
    return null;
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <button
        data-testid="refresh-data"
        onClick={loadData}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Refreshing…' : 'Refresh Data'}
      </button>

      <div 
        data-testid="data-container" 
        className="mt-4 p-4 border rounded bg-gray-50"
      >
        {data ?? 'No data yet.'}
      </div>
      
      <button
        onClick={() => authService.logout()}
        className="mt-6 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
      >
        Logout
      </button>
    </div>
  );
}
