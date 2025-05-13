// Use our custom router implementation for tests
// This allows us to export either the real Next.js router or our test mock
// depending on the environment
import { useRouter as nextUseRouter } from "next/navigation";
import { useRouter as testUseRouter } from "../__tests__/test-utils/RouterWrapper";

// Export the correct implementation based on environment
export const useRouter = () => ({
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  prefetch: vi.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
  events: {
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  }
});

export const usePathname = () => '/';
export const useSearchParams = () => new URLSearchParams();
