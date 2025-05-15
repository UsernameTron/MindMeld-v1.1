// User schema
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'user' | 'admin';
  createdAt: string;
  updatedAt: string;
}
