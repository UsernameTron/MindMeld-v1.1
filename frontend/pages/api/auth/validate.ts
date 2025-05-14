import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API validate.ts: Request received, method:', req.method);
  
  if (req.method !== 'GET') {
    console.log('API validate.ts: Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const authToken = req.cookies.auth_token;
    console.log('API validate.ts: Auth token present:', !!authToken);
    
    if (!authToken) {
      console.log('API validate.ts: No auth token in cookies');
      return res.status(401).json({ message: 'Not authenticated' });
    }

    // Verify the token
    console.log('API validate.ts: Verifying token');
    const payload = verifyToken(authToken);
    console.log('API validate.ts: Token verification result:', !!payload);
    
    if (!payload) {
      console.log('API validate.ts: Invalid or expired token');
      return res.status(401).json({ message: 'Invalid or expired token' });
    }

    // Token is valid
    console.log('API validate.ts: Token is valid for user:', payload.email);
    res.status(200).json({
      valid: true,
      message: 'Session is valid',
      user: {
        userId: payload.userId,
        email: payload.email
      }
    });
  } catch (error) {
    console.error('API validate.ts: Token validation error:', error);
    res.status(401).json({ message: 'Authentication failed' });
  }
}
