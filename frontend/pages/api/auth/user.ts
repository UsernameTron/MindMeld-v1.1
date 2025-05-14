import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API user.ts: Request received, method:', req.method);
  
  if (req.method !== 'GET') {
    console.log('API user.ts: Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Extract the auth token from cookies
  const authToken = req.cookies.auth_token;
  console.log('API user.ts: Auth token present:', !!authToken);
  
  if (!authToken) {
    console.log('API user.ts: No auth_token cookie found');
    return res.status(401).json({ message: 'Not authenticated' });
  }

  try {
    // Verify the auth token
    console.log('API user.ts: Verifying token');
    const payload = verifyToken(authToken);
    
    if (!payload) {
      console.log('API user.ts: Invalid or expired token');
      return res.status(401).json({ message: 'Invalid authentication' });
    }

    console.log('API user.ts: Token verified for user:', payload.email);

    // Check if it's our test user (demo only)
    let userName = 'User';
    if (payload.email === 'test@example.com') {
      userName = 'Test User';
    }

    // Return user profile data
    // In a real application, you would fetch more data from a database
    const userData = {
      id: payload.userId,
      name: userName,
      email: payload.email
    };
    
    console.log('API user.ts: Returning user profile:', userData);
    res.status(200).json(userData);
  } catch (error) {
    console.error('API user.ts: Error processing request:', error);
    res.status(401).json({ message: 'Authentication failed' });
  }
}