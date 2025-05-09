import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Clear all auth cookies
  res.setHeader('Set-Cookie', [
    'auth_token=; HttpOnly; Path=/; Max-Age=0',
    'refresh_token=; HttpOnly; Path=/; Max-Age=0'
  ]);

  res.status(200).json({ message: 'Logged out successfully' });
}
