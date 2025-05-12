import { vi } from 'vitest';

export const isTokenExpired = vi.fn().mockReturnValue(false);
export const decodeToken = vi.fn().mockReturnValue({ userId: 'mockUserId', role: 'user' });

export function resetJwtMocks() {
  isTokenExpired.mockReset().mockReturnValue(false);
  decodeToken.mockReset().mockReturnValue({ userId: 'mockUserId', role: 'user' });
}
