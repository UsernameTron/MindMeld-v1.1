import React from 'react';
import { Navigation } from './Navigation';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="container mx-auto p-4 md:p-6">
        {children}
      </main>
    </div>
  );
};
