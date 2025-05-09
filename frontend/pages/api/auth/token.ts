import type { NextApiRequest, NextApiResponse } from 'next';
import { generateAccessToken, generateRefreshToken } from '../../../src/utils/jwt';

// In a real app, you'd verify credentials against a database
// Here we're setting up a simple demo that always succeeds
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { email, password } = req.body;

  // In a production app, validate credentials against database
  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  // For demo purposes - in a real app, verify against database
  // In this demo, we'll accept any non-empty email and password
  const userId = `user-${Date.now()}`; // Simulate a user ID

  // Generate JWT tokens
  const accessToken = generateAccessToken({ userId, email });
  const refreshToken = generateRefreshToken({ userId, email });

  // Set JWT token in HTTP-only cookie for security
  res.setHeader('Set-Cookie', [
    `auth_token=${accessToken}; HttpOnly; Path=/; Max-Age=3600`,  // 1 hour
    `refresh_token=${refreshToken}; HttpOnly; Path=/; Max-Age=604800`  // 7 days
  ]);

  res.status(200).json({ message: 'Authenticated successfully' });
}
