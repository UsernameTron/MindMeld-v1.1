import { test, expect, describe, vi, beforeAll, afterAll } from 'vitest';
import { mockApiClient } from '../mocks/apiClient';
import { authService } from '../../src/services/authService';
import jwt from 'jsonwebtoken';

// Patch authService to use mockApiClient for all requests in tests
import * as authServiceModule from '../../src/services/authService';
const realApiClient = authServiceModule.authService;

describe('JWT Lifecycle', () => {
  beforeAll(() => {
    // Attach mockApiClient to globalThis for authService to pick up
    (globalThis as any).mockApiClient = mockApiClient;

    // Patch global apiClient to use mockApiClient in tests
    (globalThis as any).apiClient = mockApiClient;
    // Add a get method to mockApiClient for validateSession
    mockApiClient.get = vi.fn();
  });

  afterAll(() => {
    delete (globalThis as any).mockApiClient;
    delete (globalThis as any).apiClient;
    // Use optional chaining to avoid TS2790 error
    if ((mockApiClient as any).get) {
      delete (mockApiClient as any).get;
    }
  });

  test('should detect expired tokens', async () => {
    const expiredToken = jwt.sign(
      { sub: 'test-user', exp: Math.floor(Date.now() / 1000) - 60 },
      'test-secret'
    );
    document.cookie = `auth_token=${expiredToken}; path=/`;

    mockApiClient.post.mockResolvedValueOnce({
      data: { token: 'new-valid-token' },
      headers: {
        'set-cookie': ['auth_token=new-valid-token; HttpOnly; Secure; Path=/']
      }
    });

    const result = await authService.validateSession();

    expect(mockApiClient.post).toHaveBeenCalledWith('/auth/refresh');
    expect(result).toBe(true);
  });

  test('should redirect on malformed tokens', async () => {
    document.cookie = 'auth_token=invalid-token; path=/';

    mockApiClient.post.mockRejectedValueOnce({ response: { status: 401 } });

    const mockNavigate = vi.fn();
    (window as any).useNavigate = mockNavigate;

    await authService.validateSession();

    expect(mockNavigate).toHaveBeenCalledWith('/login');
    delete (window as any).useNavigate;
  });
});
