import type { NextApiRequest, NextApiResponse } from 'next';
import { generateAccessToken, verifyToken } from '../../../src/utils/jwt';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API refresh.ts: Request received, method:', req.method);
  
  // Handle OPTIONS for CORS preflight requests
  if (req.method === 'OPTIONS') {
    console.log('API refresh.ts: Handling OPTIONS request for CORS');
    return res.status(200).end();
  }
  
  // Only allow POST requests for token refresh
  if (req.method !== 'POST') {
    console.log('API refresh.ts: Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    console.log('API refresh.ts: Processing token refresh request');
    
    // Get refresh token from cookies
    const refreshToken = req.cookies.refresh_token;
    console.log('API refresh.ts: Refresh token present:', !!refreshToken);
    
    if (!refreshToken) {
      console.log('API refresh.ts: No refresh_token cookie found');
      return res.status(401).json({ message: 'No refresh token provided' });
    }

    // Verify the refresh token
    console.log('API refresh.ts: Verifying refresh token');
    const payload = verifyToken(refreshToken);
    
    if (!payload) {
      console.log('API refresh.ts: Invalid or expired refresh token');
      return res.status(401).json({ message: 'Invalid or expired refresh token' });
    }

    console.log('API refresh.ts: Refresh token valid, generating new access token');
    
    // Generate a new access token
    const accessToken = generateAccessToken({ 
      userId: payload.userId, 
      email: payload.email 
    });

    // Determine if we're in production
    const isProduction = process.env.NODE_ENV === 'production';
    
    // Set HTTP-only cookie with secure attributes for the new access token
    res.setHeader('Set-Cookie', [
      `auth_token=${accessToken}; HttpOnly; Path=/; Max-Age=3600; SameSite=Strict${isProduction ? '; Secure' : ''}`
    ]);

    console.log('API refresh.ts: New access token generated successfully');
    
    // Return success with the new token
    res.status(200).json({
      message: 'Token refreshed successfully',
      accessToken // Also return the token in the response for client-side storage if needed
    });
  } catch (error) {
    console.error('API refresh.ts: Error processing request:', error);
    res.status(500).json({ message: 'Token refresh failed' });
  }
}
