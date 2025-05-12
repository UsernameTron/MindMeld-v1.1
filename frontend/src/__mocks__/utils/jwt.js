import { vi } from 'vitest';

export const isTokenExpired = vi.fn().mockReturnValue(false);
export const decodeToken = vi.fn().mockReturnValue({ userId: 'mockUserId', role: 'user' });
export const verifyToken = vi.fn().mockImplementation((token) => {
  if (token === 'invalid-token') return null;
  return { userId: 'mockUserId', email: 'test@example.com' };
});
export const generateAccessToken = vi.fn().mockReturnValue('mock-access-token');
export const generateRefreshToken = vi.fn().mockReturnValue('mock-refresh-token');
export const signAccessToken = vi.fn().mockReturnValue('mock-access-token');
export const verifyRefreshToken = vi.fn().mockImplementation((token) => {
  if (token === 'valid-refresh-token' || token === 'mock-refresh-token') {
    return { userId: '123' };
  }
  return null;
});

export function resetJwtMocks() {
  isTokenExpired.mockReset().mockReturnValue(false);
  decodeToken.mockReset().mockReturnValue({ userId: 'mockUserId', role: 'user' });
  verifyToken.mockReset().mockImplementation((token) => {
    if (token === 'invalid-token') return null;
    return { userId: 'mockUserId', email: 'test@example.com' };
  });
  generateAccessToken.mockReset().mockReturnValue('mock-access-token');
  generateRefreshToken.mockReset().mockReturnValue('mock-refresh-token');
  signAccessToken.mockReset().mockReturnValue('mock-access-token');
  verifyRefreshToken.mockReset().mockImplementation((token) => {
    if (token === 'valid-refresh-token' || token === 'mock-refresh-token') {
      return { userId: '123' };
    }
    return null;
  });
}

export default {
  isTokenExpired,
  decodeToken,
  verifyToken,
  generateAccessToken,
  generateRefreshToken,
  signAccessToken,
  verifyRefreshToken,
  resetJwtMocks
};