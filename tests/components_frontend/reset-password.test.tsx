import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ResetPasswordPage from '../../pages/reset-password';
import '@testing-library/jest-dom';
import { useRouter } from 'next/router';
import type { NextRouter } from 'next/router';

// Mock Next.js router
jest.mock('next/router', () => ({
    useRouter: jest.fn(),
}));

// Mock fetch for API calls
global.fetch = jest.fn();
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
const mockRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('Reset Password Page', () => {
    beforeEach(() => {
        jest.resetAllMocks();

        // Setup router mock
        mockRouter.mockImplementation(() => ({
            route: '/reset-password',
            pathname: '/reset-password',
            asPath: '/reset-password',
            basePath: '',
            isLocaleDomain: false,
            query: { token: 'test-token', email: 'test@example.com' },
            push: jest.fn(),
            replace: jest.fn(),
            reload: jest.fn(),
            back: jest.fn(),
            forward: jest.fn(),
            prefetch: jest.fn().mockResolvedValue(undefined),
            beforePopState: jest.fn(),
            events: {
                on: jest.fn(),
                off: jest.fn(),
                emit: jest.fn(),
            },
            isFallback: false,
            isReady: true,
            isPreview: false,
        }));

        // Default valid token response
        mockFetch.mockImplementation(async (url) => {
            if (url.toString().includes('?token=')) {
                return {
                    ok: true,
                    json: async () => ({ valid: true }),
                } as Response;
            }

            return {
                ok: true,
                json: async () => ({ message: 'Password updated successfully' }),
            } as Response;
        });
    });

    it('validates token when component loads', async () => {
        render(<ResetPasswordPage />);

        // Should show loading state first
        expect(screen.getByText(/verifying reset token/i)).toBeInTheDocument();

        // Then should show the form
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
        });

        expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/auth/resetPassword?token=test-token&email=test%40example.com')
        );
    });

    it('shows error message for invalid token', async () => {
        // Mock invalid token response
        mockFetch.mockImplementation(async () => ({
            ok: true,
            json: async () => ({ valid: false }),
        } as Response));

        render(<ResetPasswordPage />);

        expect(await screen.findByText(/invalid or expired password reset link/i)).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /back to login/i })).toBeInTheDocument();
    });

    it('validates passwords match before submission', async () => {
        render(<ResetPasswordPage />);

        // Wait for token validation to complete
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        });

        const newPasswordInput = screen.getByLabelText(/new password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
        const submitButton = screen.getByRole('button', { name: /reset password/i });

        // Enter non-matching passwords
        fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
        expect(mockFetch).not.toHaveBeenCalledWith(
            expect.anything(),
            expect.objectContaining({ method: 'PUT' })
        );
    });

    it('validates password strength', async () => {
        render(<ResetPasswordPage />);

        // Wait for token validation to complete
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        });

        const newPasswordInput = screen.getByLabelText(/new password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
        const submitButton = screen.getByRole('button', { name: /reset password/i });

        // Enter short password
        fireEvent.change(newPasswordInput, { target: { value: 'short' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'short' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/password must be at least 8 characters long/i)).toBeInTheDocument();
    });

    it('submits form and shows success message', async () => {
        const mockPush = jest.fn();
        mockRouter.mockImplementation(() => ({
            route: '/reset-password',
            pathname: '/reset-password',
            asPath: '/reset-password',
            basePath: '',
            isLocaleDomain: false,
            query: { token: 'test-token', email: 'test@example.com' },
            push: mockPush,
            replace: jest.fn(),
            reload: jest.fn(),
            back: jest.fn(),
            forward: jest.fn(),
            prefetch: jest.fn().mockResolvedValue(undefined),
            beforePopState: jest.fn(),
            events: {
                on: jest.fn(),
                off: jest.fn(),
                emit: jest.fn(),
            },
            isFallback: false,
            isReady: true,
            isPreview: false,
        }));

        // Mock successful password update
        mockFetch.mockImplementation(async (url) => {
            if (url.toString().includes('?token=')) {
                return {
                    ok: true,
                    json: async () => ({ valid: true }),
                } as Response;
            }

            return {
                ok: true,
                json: async () => ({ message: 'Password updated successfully' }),
            } as Response;
        });

        render(<ResetPasswordPage />);

        // Wait for token validation to complete
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        });

        const newPasswordInput = screen.getByLabelText(/new password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
        const submitButton = screen.getByRole('button', { name: /reset password/i });

        fireEvent.change(newPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/password has been reset successfully/i)).toBeInTheDocument();

        expect(mockFetch).toHaveBeenCalledWith('/api/auth/resetPassword', expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify({
                email: 'test@example.com',
                token: 'test-token',
                newPassword: 'NewSecurePassword123!'
            }),
        }));

        // Wait for redirect timeout
        jest.advanceTimersByTime(3000);
        expect(mockPush).toHaveBeenCalledWith('/login');
    });

    it('handles API errors during password reset', async () => {
        // First validation succeeds, but update fails
        mockFetch.mockImplementation(async (url) => {
            if (url.toString().includes('?token=')) {
                return {
                    ok: true,
                    json: async () => ({ valid: true }),
                } as Response;
            }

            return {
                ok: false,
                json: async () => ({ message: 'Invalid or expired token' }),
            } as Response;
        });

        render(<ResetPasswordPage />);

        // Wait for token validation to complete
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        });

        const newPasswordInput = screen.getByLabelText(/new password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
        const submitButton = screen.getByRole('button', { name: /reset password/i });

        fireEvent.change(newPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/invalid or expired token/i)).toBeInTheDocument();
    });

    it('handles network errors', async () => {
        // Mock token validation to succeed
        mockFetch.mockImplementationOnce(async () => ({
            ok: true,
            json: async () => ({ valid: true }),
        } as Response));

        // But password update throws network error
        mockFetch.mockImplementationOnce(() => {
            throw new Error('Network error');
        });

        render(<ResetPasswordPage />);

        // Wait for token validation to complete
        await waitFor(() => {
            expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        });

        const newPasswordInput = screen.getByLabelText(/new password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);
        const submitButton = screen.getByRole('button', { name: /reset password/i });

        fireEvent.change(newPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'NewSecurePassword123!' } });
        fireEvent.click(submitButton);

        expect(await screen.findByText(/network error occurred/i)).toBeInTheDocument();
    });
});
