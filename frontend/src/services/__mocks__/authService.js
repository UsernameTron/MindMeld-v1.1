export const authService = {
  login: vi.fn().mockImplementation(async (email, password) => {
    console.log('[AuthService] Using mock login implementation');
    return {
      token: 'mock-token',
      refreshToken: 'mock-refresh-token',
      user: {
        id: '123',
        email,
        name: 'Test User',
        passwordChangeRequired: false,
        isVerified: true,
        lastLogin: new Date().toISOString(),
        role: 'user'
      }
    };
  }),
  logout: vi.fn().mockResolvedValue(undefined),
  refreshToken: vi.fn().mockResolvedValue('mock-refresh-token'),
  isAuthenticated: vi.fn().mockReturnValue(true)
};
