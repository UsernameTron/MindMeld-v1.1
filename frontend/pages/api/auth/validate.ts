import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const authToken = req.cookies.auth_token;
  
  if (!authToken) {
    return res.status(401).json({ message: 'Not authenticated' });
  }

  // Verify the token
  const payload = verifyToken(authToken);
  if (!payload) {
    return res.status(401).json({ message: 'Invalid or expired token' });
  }

  // Return user info for frontend use
  res.status(200).json({
    message: 'Session is valid',
    user: {
      userId: payload.userId,
      email: payload.email
    }
  });
}
