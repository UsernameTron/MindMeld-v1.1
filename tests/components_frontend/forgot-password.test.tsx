import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ForgotPasswordPage from '../../pages/forgot-password';
import '@testing-library/jest-dom';

// Mock fetch for API calls
global.fetch = jest.fn();
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('Forgot Password Page', () => {
    beforeEach(() => {
        jest.resetAllMocks();

        // Default mock implementation
        mockFetch.mockImplementation(async () => ({
            ok: true,
            json: async () => ({ message: 'Password reset email sent' }),
        } as Response));
    });

    it('renders the forgot password form', () => {
        render(<ForgotPasswordPage />);

        expect(screen.getByRole('heading', { name: /forgot password/i })).toBeInTheDocument();
        expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /back to login/i })).toBeInTheDocument();
    });

    it('validates email input', async () => {
        render(<ForgotPasswordPage />);

        const emailInput = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /send reset link/i });

        // Try to submit without filling the email
        fireEvent.click(submitButton);

        // Should show HTML5 validation error
        await waitFor(() => {
            expect(emailInput).toBeInvalid();
        });
    });

    it('displays loading state during form submission', async () => {
        // Delay the mock response to show loading state
        mockFetch.mockImplementation(async () => {
            await new Promise(resolve => setTimeout(resolve, 100));
            return {
                ok: true,
                json: async () => ({ message: 'Password reset email sent' }),
            } as Response;
        });

        render(<ForgotPasswordPage />);

        const emailInput = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /send reset link/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/sending/i)).toBeInTheDocument();
    });

    it('shows success message after successful submission', async () => {
        render(<ForgotPasswordPage />);

        const emailInput = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /send reset link/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/if an account exists/i)).toBeInTheDocument();
        expect(mockFetch).toHaveBeenCalledWith('/api/auth/resetPassword', expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({ email: 'test@example.com' }),
        }));
    });

    it('shows debug reset link in development environment', async () => {
        // Save the original environment
        const originalEnv = process.env.NODE_ENV;

        try {
            // Set to development
            Object.defineProperty(process.env, 'NODE_ENV', {
                value: 'development',
                configurable: true
            });

            // Mock API response with debug data
            mockFetch.mockImplementation(async () => ({
                ok: true,
                json: async () => ({
                    message: 'Password reset email sent',
                    debug: {
                        resetToken: 'test-token-12345',
                        resetLink: '/reset-password?token=test-token-12345&email=test%40example.com'
                    }
                }),
            } as Response));

            render(<ForgotPasswordPage />);

            const emailInput = screen.getByLabelText(/email address/i);
            const submitButton = screen.getByRole('button', { name: /send reset link/i });

            fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
            fireEvent.click(submitButton);

            expect(await screen.findByText(/debug: password reset link/i)).toBeInTheDocument();
            expect(await screen.findByText(/\/reset-password/)).toBeInTheDocument();
        } finally {
            // Restore the original environment
            Object.defineProperty(process.env, 'NODE_ENV', {
                value: originalEnv,
                configurable: true
            });
        }
    });

    it('handles API errors', async () => {
        // Mock API error response
        mockFetch.mockImplementation(async () => ({
            ok: false,
            json: async () => ({ message: 'Server error' }),
        } as Response));

        render(<ForgotPasswordPage />);

        const emailInput = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /send reset link/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/server error/i)).toBeInTheDocument();
    });

    it('handles network errors', async () => {
        // Mock network error
        mockFetch.mockImplementation(() => {
            throw new Error('Network error');
        });

        render(<ForgotPasswordPage />);

        const emailInput = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /send reset link/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/failed to connect/i)).toBeInTheDocument();
    });
});
