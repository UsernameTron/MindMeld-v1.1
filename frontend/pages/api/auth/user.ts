import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Extract the auth token from cookies
  const authToken = req.cookies.auth_token;
  
  if (!authToken) {
    return res.status(401).json({ message: 'Not authenticated' });
  }

  try {
    // Verify the auth token
    const payload = verifyToken(authToken);
    if (!payload) {
      return res.status(401).json({ message: 'Invalid authentication' });
    }

    // Return user profile data
    // In a real application, you would fetch this from a database
    res.status(200).json({
      id: payload.userId,
      name: 'User',
      email: payload.email
    });
  } catch (error) {
    console.error('Auth error:', error);
    res.status(401).json({ message: 'Authentication failed' });
  }
}