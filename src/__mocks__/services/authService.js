import { vi } from 'vitest';

const MOCK_TOKEN = 'mock-jwt-token';

export const authService = {
  login: vi.fn().mockImplementation(async (username, password) => {
    if (username === 'testuser@example.com' && password === 'password123') {
      localStorage.setItem('token', MOCK_TOKEN);
      return { token: MOCK_TOKEN, user: { id: '123', email: username, name: 'Test User' } };
    }
    throw new Error('Invalid username or password');
  }),
  logout: vi.fn().mockResolvedValue(undefined),
  refreshToken: vi.fn().mockResolvedValue('new-valid-token'),
  isAuthenticated: vi.fn().mockReturnValue(true),
};

export function resetAuthServiceMocks() {
  Object.values(authService).forEach(mock => {
    if (typeof mock === 'function' && mock.mockReset) {
      mock.mockReset();
    }
  });
  authService.login.mockImplementation(async (username, password) => {
    if (username === 'testuser@example.com' && password === 'password123') {
      localStorage.setItem('token', MOCK_TOKEN);
      return { token: MOCK_TOKEN, user: { id: '123', email: username, name: 'Test User' } };
    }
    throw new Error('Invalid username or password');
  });
  authService.isAuthenticated.mockReturnValue(false);
}
