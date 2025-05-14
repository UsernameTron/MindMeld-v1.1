import type { NextApiRequest, NextApiResponse } from 'next';
import { generateAccessToken, generateRefreshToken } from '../../../src/utils/jwt';

// In a real app, you'd verify credentials against a database
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // For CORS preflight requests
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const { email, password } = req.body;

    // Basic validation
    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required' });
    }

    // For demo purposes - in a real app, verify against database
    // In this demo, we'll accept any non-empty email and password
    const userId = `user-${Date.now()}`; // Simulate a user ID

    // Generate JWT tokens
    const accessToken = generateAccessToken({ userId, email });
    const refreshToken = generateRefreshToken({ userId, email });

    // Determine if we're in production
    const isProduction = process.env.NODE_ENV === 'production';
    
    // Set HTTP-only cookies with secure attributes
    res.setHeader('Set-Cookie', [
      `auth_token=${accessToken}; HttpOnly; Path=/; Max-Age=3600; SameSite=Strict${isProduction ? '; Secure' : ''}`,
      `refresh_token=${refreshToken}; HttpOnly; Path=/; Max-Age=604800; SameSite=Strict${isProduction ? '; Secure' : ''}`
    ]);

    // Return user information
    res.status(200).json({ 
      message: 'Authenticated successfully',
      user: {
        id: userId,
        email: email,
        name: email.split('@')[0] // Simple name extraction from email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Authentication failed' });
  }
}
