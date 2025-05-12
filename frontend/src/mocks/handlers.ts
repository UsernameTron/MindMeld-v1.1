import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('/api/auth/token', () => {
    return HttpResponse.json({
      token: 'mock-jwt-token',
      refreshToken: 'mock-refresh-token',
      user: {
        id: '123',
        email: 'testuser@example.com',
        name: 'Test User',
        passwordChangeRequired: false,
        isVerified: true,
        lastLogin: new Date().toISOString(),
        role: 'user',
      },
    });
  }),
];
