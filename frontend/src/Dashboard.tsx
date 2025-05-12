import React, { useEffect, useState } from 'react';
import { DashboardLayout } from './DashboardLayout';
import { Card } from './components/ui/Card/Card';
import { LoadingIndicator } from './components/LoadingIndicator';
import { ErrorDisplay } from './components/ErrorDisplay';
import { apiClient } from './services/apiClient';

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await apiClient.get('/dashboard/summary');
        setDashboardData(data.data);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Unable to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center py-12">
          <LoadingIndicator variant="pulse" />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !dashboardData) {
    return (
      <DashboardLayout>
        <ErrorDisplay title="Dashboard Error" message={error || 'Failed to load dashboard'} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <h2 className="text-lg font-medium mb-2">Analytics</h2>
          <p>Total Users: {dashboardData.totalUsers}</p>
          <p>Active Sessions: {dashboardData.activeSessions}</p>
        </Card>
        <Card>
          <h2 className="text-lg font-medium mb-2">Recent Activity</h2>
          <ul className="space-y-2">
            {dashboardData.recentActivity.map((activity: string, index: number) => (
              <li key={index}>{activity}</li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="text-lg font-medium mb-2">Profile</h2>
          <p>Welcome back, {dashboardData.userName}!</p>
          <p>Last login: {new Date(dashboardData.lastLogin).toLocaleString()}</p>
        </Card>
      </div>
    </DashboardLayout>
  );
};
