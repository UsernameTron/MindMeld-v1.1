import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API logout.ts: Request received, method:', req.method);

  // Handle OPTIONS for CORS preflight requests
  if (req.method === 'OPTIONS') {
    console.log('API logout.ts: Handling OPTIONS request for CORS');
    return res.status(200).end();
  }
  
  // Only allow POST requests for logout
  if (req.method !== 'POST') {
    console.log('API logout.ts: Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    console.log('API logout.ts: Processing logout request');
    
    // Check if user was authenticated
    const authToken = req.cookies.auth_token;
    console.log('API logout.ts: User had auth token:', !!authToken);
    
    // Determine if we're in production
    const isProduction = process.env.NODE_ENV === 'production';
    console.log('API logout.ts: Running in production mode:', isProduction);
    
    // Clear all auth cookies with secure attributes
    const cookies = [
      `auth_token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict${isProduction ? '; Secure' : ''}`,
      `refresh_token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict${isProduction ? '; Secure' : ''}`
    ];
    
    console.log('API logout.ts: Setting expired cookies, count:', cookies.length);
    res.setHeader('Set-Cookie', cookies);

    console.log('API logout.ts: Logout successful');
    res.status(200).json({ message: 'Logged out successfully' });
  } catch (error) {
    console.error('API logout.ts: Logout error:', error);
    res.status(500).json({ message: 'Logout failed' });
  }
}
