import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../../context/AuthContext';

export interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const router = useRouter();
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  // Navigation items
  const navItems = [
    {
      label: 'Home',
      href: '/dashboard',
    },
    {
      label: 'Code Analyzer',
      href: '/analyze',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">MindMeld</h1>
          <div className="flex items-center">
            {isAuthenticated ? (
              <>
                <span className="mr-4">{user?.name || user?.email}</span>
                <button 
                  onClick={handleLogout}
                  className="px-3 py-2 rounded text-sm text-gray-700 hover:bg-gray-100"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link href="/login" className="px-3 py-2 rounded text-sm text-gray-700 hover:bg-gray-100">
                Login
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Main layout: sidebar + content */}
      <div className="flex flex-1 min-h-0">
        {/* Sidebar */}
        <nav className="w-56 bg-gray-100 border-r p-4 hidden md:block">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const isActive = router.pathname === item.href || (item.href !== '/dashboard' && router.pathname.startsWith(item.href));
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`block px-3 py-2 rounded transition-colors duration-150 text-base font-medium ${
                      isActive
                        ? 'bg-blue-500 text-white'
                        : 'text-gray-800 hover:bg-gray-200'
                    }`}
                  >
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Mobile sidebar (optional, placeholder) */}
        {/* <nav className="md:hidden ..."> ... </nav> */}

        {/* Main content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
