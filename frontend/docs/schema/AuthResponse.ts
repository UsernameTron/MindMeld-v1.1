// AuthResponse schema
export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: {
    id: string;
    username: string;
    email: string;
    role: 'user' | 'admin';
  };
  expiresIn: number; // seconds
}
