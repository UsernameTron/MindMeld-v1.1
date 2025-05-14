import { ReactNode } from 'react';
// Only import Dashboard if it exists, otherwise use a placeholder
let Dashboard: React.ComponentType = () => null;
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  Dashboard = require('../pages/dashboard').default;
} catch {}
// Use a placeholder for Analyze (or import if it exists)
const Analyze: React.ComponentType = () => null;
// Use a placeholder for Login (or import if it exists)
const Login: React.ComponentType = () => null;

export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  requiresAuth: boolean;
  title: string;
  navLabel?: string; // Included in navigation
  icon?: ReactNode; // Optional icon for nav
}

export const routes: Record<string, RouteConfig> = {
  dashboard: {
    path: '/dashboard',
    component: Dashboard,
    requiresAuth: true,
    title: 'Dashboard',
    navLabel: 'Dashboard'
  },
  analyze: {
    path: '/analyze',
    component: Analyze,
    requiresAuth: true,
    title: 'Code Analyzer',
    navLabel: 'Code Analyzer'
  },
  login: {
    path: '/login',
    component: Login,
    requiresAuth: false,
    title: 'Login'
  }
};

// Utility to check if a route requires authentication
export const routeRequiresAuth = (path: string): boolean => {
  const route = Object.values(routes).find(r => r.path === path);
  return route ? route.requiresAuth : false;
};
