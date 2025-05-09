import { vi } from 'vitest';

// Simple mock for apiClient to be used in Vitest tests
export const mockApiClient = {
  post: vi.fn(),
  get: vi.fn()
};
