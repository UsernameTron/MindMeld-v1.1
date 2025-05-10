import type { NextApiRequest, NextApiResponse } from 'next';
import { signAccessToken, verifyRefreshToken } from '../../../utils/jwt';
import { setAuthCookie } from '../../../utils/setAuthCookie';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Try to get refresh token from cookies or body
  const refreshToken = req.cookies.refreshToken || req.body?.refreshToken;
  if (!refreshToken) {
    return res.status(401).json({ error: 'No refresh token provided' });
  }

  const user = verifyRefreshToken(refreshToken);
  if (!user) {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }

  // Issue new access token
  const accessToken = signAccessToken({ sub: user.userId });
  setAuthCookie(res, accessToken);
  return res.status(200).json({ access_token: accessToken });
}
