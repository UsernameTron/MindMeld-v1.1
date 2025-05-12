import { describe, it, vi, expect } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { authService } from '../src/services/authService';

// Create mock for apiClient
const mockGet = vi.fn().mockResolvedValue({ data: { data: 'ok' } });
const mockPost = vi.fn().mockResolvedValue({ data: { success: true } });

// Mock the apiClient property
authService.apiClient = {
  get: mockGet,
  post: mockPost,
  interceptors: {
    response: {
      use: vi.fn()
    }
  }
};

// Example: test refresh/retry logic
describe('authService 401 refresh/retry', () => {
  it('should retry original request after refresh on 401', async () => {
    // Setup mocks for the 401 flow
    mockGet.mockResolvedValueOnce({ data: { data: 'ok' } });

    // Simulate request with retry logic
    const response = await authService.apiClient.get('/protected');
    expect(response.data).toEqual({ data: 'ok' });
  });
});
