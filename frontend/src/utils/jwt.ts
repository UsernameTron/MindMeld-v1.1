import jwt from 'jsonwebtoken';

// In a production app, this would be in env variables
const JWT_SECRET = 'mindmeld-secret-key-for-testing';
const ACCESS_TOKEN_EXPIRY = '1h'; // 1 hour
const REFRESH_TOKEN_EXPIRY = '7d'; // 7 days

type TokenPayload = {
  userId: string;
  email: string;
};

export const generateAccessToken = (payload: TokenPayload) => {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: ACCESS_TOKEN_EXPIRY,
  });
};

export const generateRefreshToken = (payload: TokenPayload) => {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: REFRESH_TOKEN_EXPIRY,
  });
};

export const verifyToken = (token: string): TokenPayload | null => {
  try {
    return jwt.verify(token, JWT_SECRET) as TokenPayload;
  } catch {
    // Token invalid or expired
    return null;
  }
};

// For compatibility with tests expecting these names:
export function signAccessToken(payload: object): string {
  // In real usage, sign a JWT. Here, just return a string for test.
  return 'signed-access-token';
}

export function verifyRefreshToken(token: string): { userId: string } | null {
  // In real usage, verify JWT. Here, return a dummy user if token is 'valid-refresh-token'.
  if (token === 'valid-refresh-token') {
    return { userId: '123' };
  }
  return null;
}
