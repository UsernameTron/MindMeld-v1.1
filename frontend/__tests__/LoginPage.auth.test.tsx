import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '../pages/login';

// Mock the authService and apiClient
vi.mock('@/services/authService', () => {
  const actual = vi.importActual('@/services/authService');
  return {
    ...actual,
    createAuthService: () => ({
      login: jest.fn((email, password) => {
        if (email === 'testuser@example.com' && password === 'password123') {
          window.localStorage.setItem('token', 'mock-jwt-token');
          return Promise.resolve(true);
        }
        return Promise.resolve(false);
      }),
    }),
  };
});

vi.mock('@/services/api/apiClient', () => ({
  apiClient: {},
}));

describe('LoginPage authentication flow', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('logs in successfully with correct credentials', async () => {
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'testuser@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(window.localStorage.getItem('token')).toBe('mock-jwt-token');
    });
    // Optionally check for redirect (window.location.href)
  });

  it('shows error for invalid credentials', async () => {
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'wronguser@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'any' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/invalid email or password/i);
    });
  });

  it('shows validation error for invalid email format', async () => {
    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'notanemail' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    // The browser's built-in validation will prevent submission, so check for required attribute
    expect(screen.getByLabelText(/email/i)).toBeInvalid();
  });
});
