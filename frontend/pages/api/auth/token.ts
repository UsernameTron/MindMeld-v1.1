import type { NextApiRequest, NextApiResponse } from 'next';
import { generateAccessToken, generateRefreshToken } from '../../../src/utils/jwt';

// For testing - in a real app, you'd verify against a database
const TEST_USER = {
  email: "test@example.com",
  password: "Test123!",
  id: "test-user-1",
  name: "Test User"
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API token.ts: Request received, method:', req.method);
  
  // Handle OPTIONS for CORS preflight requests
  if (req.method === 'OPTIONS') {
    console.log('API token.ts: Handling OPTIONS request for CORS');
    return res.status(200).end();
  }
  
  // Only allow POST requests for authentication
  if (req.method !== 'POST') {
    console.log('API token.ts: Method not allowed:', req.method);
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    console.log('API token.ts: Processing login request');
    const { email, password } = req.body;
    console.log('API token.ts: Email provided:', email, 'Password provided:', password ? '[REDACTED]' : 'missing');

    // Basic validation
    if (!email || !password) {
      console.log('API token.ts: Missing credentials');
      return res.status(400).json({ message: 'Email and password are required' });
    }

    // Check for test user
    if (email === TEST_USER.email && password === TEST_USER.password) {
      console.log('API token.ts: Test user authenticated');
      const userId = TEST_USER.id;

      // Generate JWT tokens
      console.log('API token.ts: Generating tokens for test user');
      const accessToken = generateAccessToken({ userId, email });
      const refreshToken = generateRefreshToken({ userId, email });

      // Determine if we're in production
      const isProduction = process.env.NODE_ENV === 'production';
      console.log('API token.ts: Running in production mode:', isProduction);
      
      // Set HTTP-only cookies with secure attributes
      const cookies = [
        `auth_token=${accessToken}; HttpOnly; Path=/; Max-Age=3600; SameSite=Strict${isProduction ? '; Secure' : ''}`,
        `refresh_token=${refreshToken}; HttpOnly; Path=/; Max-Age=604800; SameSite=Strict${isProduction ? '; Secure' : ''}`
      ];
      console.log('API token.ts: Setting cookies, count:', cookies.length);
      res.setHeader('Set-Cookie', cookies);

      // Return success response with user data (excluding password)
      return res.status(200).json({
        message: 'Authentication successful',
        user: {
          id: TEST_USER.id,
          name: TEST_USER.name,
          email: TEST_USER.email
        }
      });
    }

    // For demo purposes - accept any other credentials with generic user info
    // In a real app, you would verify credentials against a database
    if (email && password) {
      console.log('API token.ts: Generic user authenticated');
      const userId = `user-${Date.now()}`; // Simulate a user ID

      // Generate JWT tokens
      console.log('API token.ts: Generating tokens for generic user');
      const accessToken = generateAccessToken({ userId, email });
      const refreshToken = generateRefreshToken({ userId, email });

      // Set HTTP-only cookies
      const isProduction = process.env.NODE_ENV === 'production';
      const cookies = [
        `auth_token=${accessToken}; HttpOnly; Path=/; Max-Age=3600; SameSite=Strict${isProduction ? '; Secure' : ''}`,
        `refresh_token=${refreshToken}; HttpOnly; Path=/; Max-Age=604800; SameSite=Strict${isProduction ? '; Secure' : ''}`
      ];
      res.setHeader('Set-Cookie', cookies);

      // Return success response with user data
      return res.status(200).json({
        message: 'Authentication successful',
        user: {
          id: userId,
          name: 'User',
          email
        }
      });
    }

    // If we got here, credentials are invalid
    console.log('API token.ts: Invalid credentials');
    return res.status(401).json({ message: 'Invalid email or password' });
  } catch (error) {
    console.error('API token.ts: Error processing request:', error);
    res.status(500).json({ message: 'Authentication failed due to server error' });
  }
}
