// Mock API Client
import { vi } from 'vitest';

export const apiClient = {
  request: vi.fn(),
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn()
};

export default apiClient;
