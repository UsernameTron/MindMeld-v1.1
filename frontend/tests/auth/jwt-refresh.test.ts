import { test, expect, describe, vi, beforeAll, afterAll } from 'vitest';
import { mockApiClient } from '../mocks/apiClient';
import { createAuthService } from '../../src/services/authService';
import jwt from 'jsonwebtoken';

let authService: ReturnType<typeof createAuthService>;
let realLocation: Location;

describe('JWT Lifecycle', () => {
  beforeAll(() => {
    // Save the real location so we can restore later
    realLocation = window.location;
    // Define a writable mock location
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: {
        ...realLocation,
        href: '',
        assign: vi.fn(function(url: string) { (window.location as any).href = url; })
      }
    });
    mockApiClient.get = vi.fn();
    authService = createAuthService(mockApiClient);
  });

  afterAll(() => {
    // Restore original location
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: realLocation
    });
    if ((mockApiClient as any).get) {
      delete (mockApiClient as any).get;
    }
  });

  test('should detect expired tokens', async () => {
    const expiredToken = jwt.sign(
      { sub: 'test-user', exp: Math.floor(Date.now() / 1000) - 60 },
      'test-secret'
    );
    window.localStorage.setItem('token', expiredToken);
    
    mockApiClient.get.mockRejectedValueOnce({ 
      response: { status: 401 } 
    });
    
    mockApiClient.post.mockResolvedValueOnce({
      data: { access_token: 'new-valid-token' },
    });

    const result = await authService.validateSession();

    expect(mockApiClient.get).toHaveBeenCalledWith('/auth/validate');
    expect(mockApiClient.post).toHaveBeenCalledWith('/auth/refresh');
    expect(window.localStorage.getItem('token')).toBe('new-valid-token');
    expect(result).toBe(true);
  });

  test('should redirect on malformed tokens', async () => {
    const invalidToken = 'invalid-token';
    window.localStorage.setItem('token', invalidToken);
    
    mockApiClient.get.mockRejectedValueOnce({ 
      response: { status: 401 } 
    });
    
    mockApiClient.post.mockRejectedValueOnce({ 
      response: { status: 401 } 
    });

    await authService.validateSession();

    expect(window.location.assign).toHaveBeenCalledWith('/login');
  });
});
