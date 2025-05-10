// Utility for setting cookies with proper flags
import { NextApiResponse } from 'next';
import cookie from 'cookie';

export function setAuthCookie(res: NextApiResponse, token: string) {
  const isProd = process.env.NODE_ENV === 'production' || process.env.FORCE_SECURE === 'true';
  res.setHeader(
    'Set-Cookie',
    cookie.serialize('auth_token', token, {
      httpOnly: true,
      secure: isProd,
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60, // 1 hour
    })
  );
}
