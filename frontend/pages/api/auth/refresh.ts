import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken, generateAccessToken } from '../../../src/utils/jwt';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // For CORS preflight requests
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    // Extract the refresh token from cookies
    const refreshToken = req.cookies.refresh_token;
    
    if (!refreshToken) {
      return res.status(401).json({ message: 'No refresh token found' });
    }

    // Verify the refresh token
    const payload = verifyToken(refreshToken);
    if (!payload) {
      // Clear invalid cookies with secure attributes
      const isProduction = process.env.NODE_ENV === 'production';
      res.setHeader('Set-Cookie', [
        `auth_token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict${isProduction ? '; Secure' : ''}`,
        `refresh_token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict${isProduction ? '; Secure' : ''}`
      ]);
      return res.status(401).json({ message: 'Invalid refresh token' });
    }

    // Generate a new access token
    const newAccessToken = generateAccessToken({
      userId: payload.userId,
      email: payload.email
    });

    // Determine if we're in production
    const isProduction = process.env.NODE_ENV === 'production';
    
    // Issue a new access token - keep the same refresh token
    res.setHeader('Set-Cookie', [
      `auth_token=${newAccessToken}; HttpOnly; Path=/; Max-Age=3600; SameSite=Strict${isProduction ? '; Secure' : ''}` // 1 hour
    ]);

    // Return the token for client-side in-memory storage
    res.status(200).json({ 
      accessToken: newAccessToken
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(401).json({ message: 'Invalid refresh token' });
  }
}
