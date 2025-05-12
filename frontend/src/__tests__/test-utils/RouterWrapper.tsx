import React from 'react';
import { vi } from 'vitest';

// Define router interface for type safety
interface RouterContextType {
  push: (url: string, options?: object) => Promise<boolean>;
  replace: (url: string, options?: object) => Promise<boolean>;
  back: () => void;
  prefetch: (url: string) => Promise<void>;
  refresh: () => void;
  pathname: string;
  query: Record<string, string | string[]>;
  asPath: string;
  route: string;
  events: {
    on: (event: string, callback: (...args: any[]) => void) => void;
    off: (event: string, callback: (...args: any[]) => void) => void;
    emit: (event: string, ...args: any[]) => void;
  };
}

// Mock navigation context
const RouterContext = React.createContext<RouterContextType>({
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  prefetch: vi.fn(),
  refresh: vi.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
  route: '/',
  events: {
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  }
});

// Export the mock useRouter hook
export const useRouter = (): RouterContextType => React.useContext(RouterContext);

// Create exported mock functions to allow testing with proper types
export const routerFunctions = {
  push: vi.fn<[string, (object | undefined)?], Promise<boolean>>().mockResolvedValue(true),
  replace: vi.fn<[string, (object | undefined)?], Promise<boolean>>().mockResolvedValue(true),
  back: vi.fn<[], void>(),
  prefetch: vi.fn<[string], Promise<void>>().mockResolvedValue(),
  refresh: vi.fn<[], void>(),
  // Reset all mock functions for testing
  resetMocks: () => {
    routerFunctions.push.mockReset();
    routerFunctions.replace.mockReset();
    routerFunctions.back.mockReset();
    routerFunctions.prefetch.mockReset();
    routerFunctions.refresh.mockReset();
  }
};

interface RouterWrapperProps {
  children: React.ReactNode;
}

// Router wrapper for testing
export const RouterWrapper: React.FC<RouterWrapperProps> = ({ children }) => {
  const mockRouter: RouterContextType = {
    ...routerFunctions, // Use the exported functions so tests can access them
    pathname: '/',
    query: {},
    asPath: '/',
    route: '/',
    events: {
      on: vi.fn<[string, (...args: any[]) => void], void>(),
      off: vi.fn<[string, (...args: any[]) => void], void>(),
      emit: vi.fn<[string, ...any[]], void>()
    }
  };

  return (
    <RouterContext.Provider value={mockRouter}>
      {children}
    </RouterContext.Provider>
  );
};
