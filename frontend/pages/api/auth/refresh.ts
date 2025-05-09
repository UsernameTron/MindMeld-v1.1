import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken, generateAccessToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Extract the refresh token from cookies
  const refreshToken = req.cookies.refresh_token;
  
  if (!refreshToken) {
    return res.status(401).json({ message: 'No refresh token found' });
  }

  // Verify the refresh token
  const payload = verifyToken(refreshToken);
  if (!payload) {
    // Clear invalid cookies
    res.setHeader('Set-Cookie', [
      'auth_token=; HttpOnly; Path=/; Max-Age=0',
      'refresh_token=; HttpOnly; Path=/; Max-Age=0'
    ]);
    return res.status(401).json({ message: 'Invalid refresh token' });
  }

  // Generate a new access token
  const newAccessToken = generateAccessToken({
    userId: payload.userId,
    email: payload.email
  });

  // Issue a new access token - keep the same refresh token
  res.setHeader('Set-Cookie', [
    `auth_token=${newAccessToken}; HttpOnly; Path=/; Max-Age=3600` // 1 hour
  ]);

  res.status(200).json({ message: 'Token refreshed successfully' });
}
