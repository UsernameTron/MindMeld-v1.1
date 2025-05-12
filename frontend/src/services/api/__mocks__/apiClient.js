export const apiClient = {
  request: vi.fn().mockResolvedValue({
    token: 'mock-token',
    refreshToken: 'mock-refresh-token',
    user: {
      id: '123',
      email: 'test@example.com',
      name: 'Test User'
    }
  }),
  setAuthToken: vi.fn()
};
