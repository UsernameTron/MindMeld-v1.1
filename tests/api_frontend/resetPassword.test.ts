import { NextApiRequest, NextApiResponse } from 'next';
import { createMocks } from 'node-mocks-http';
import resetPasswordHandler from '../../pages/api/auth/resetPassword';

// Mock crypto module
jest.mock('crypto', () => ({
    randomBytes: jest.fn(() => ({ toString: () => 'test-token-12345' }))
}));

const mockRequestResponse = (method = 'POST', body = {}, query = {}) => {
    const { req, res } = createMocks({
        method,
        body,
        query
    });
    return { req: req as NextApiRequest, res: res as NextApiResponse };
};

describe('Password Reset Handler', () => {
    beforeEach(() => {
        // Clear module cache to ensure clean test runs
        jest.resetModules();
        jest.clearAllMocks();
    });

    it('should reject requests with invalid methods', async () => {
        const { req, res } = mockRequestResponse('DELETE');

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(405);
        expect(res._getJSONData()).toEqual({
            message: 'Method not allowed'
        });
    });

    it('should require email parameter for POST requests', async () => {
        const { req, res } = mockRequestResponse('POST', {});

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(400);
        expect(res._getJSONData()).toEqual({
            message: 'Email is required'
        });
    });

    it('should generate a reset token for valid email', async () => {
        const testEmail = 'test@example.com';
        const { req, res } = mockRequestResponse('POST', { email: testEmail });

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(200);
        expect(res._getJSONData()).toHaveProperty('message', 'Password reset email sent');
        // In development mode, it should return debug info
        expect(res._getJSONData()).toHaveProperty('debug.resetToken', 'test-token-12345');
        expect(res._getJSONData()).toHaveProperty('debug.resetLink',
            expect.stringContaining(`/reset-password?token=test-token-12345&email=${encodeURIComponent(testEmail)}`));
    });

    it('should validate token via GET request', async () => {
        // First create a token
        const testEmail = 'test@example.com';
        const { req: postReq, res: postRes } = mockRequestResponse('POST', { email: testEmail });

        await resetPasswordHandler(postReq, postRes);

        // Now validate the token
        const { req: getReq, res: getRes } = mockRequestResponse('GET', {}, {
            email: testEmail,
            token: 'test-token-12345'
        });

        await resetPasswordHandler(getReq, getRes);

        expect(getRes.statusCode).toBe(200);
        expect(getRes._getJSONData()).toHaveProperty('valid', true);
    });

    it('should return invalid for non-existent tokens', async () => {
        const { req, res } = mockRequestResponse('GET', {}, {
            email: 'test@example.com',
            token: 'non-existent-token'
        });

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(200);
        expect(res._getJSONData()).toHaveProperty('valid', false);
    });

    it('should require all parameters for password reset', async () => {
        const { req, res } = mockRequestResponse('PUT', {
            email: 'test@example.com',
            // Missing token and newPassword
        });

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(400);
        expect(res._getJSONData()).toEqual({
            message: 'Email, token, and new password are required'
        });
    });

    it('should reset password with valid token', async () => {
        // First create a token
        const testEmail = 'test@example.com';
        const { req: postReq, res: postRes } = mockRequestResponse('POST', { email: testEmail });

        await resetPasswordHandler(postReq, postRes);

        // Now reset password
        const { req: putReq, res: putRes } = mockRequestResponse('PUT', {
            email: testEmail,
            token: 'test-token-12345',
            newPassword: 'NewSecurePassword123!'
        });

        await resetPasswordHandler(putReq, putRes);

        expect(putRes.statusCode).toBe(200);
        expect(putRes._getJSONData()).toEqual({
            message: 'Password updated successfully'
        });
    });

    it('should reject password reset with invalid token', async () => {
        const { req, res } = mockRequestResponse('PUT', {
            email: 'test@example.com',
            token: 'invalid-token',
            newPassword: 'NewPassword123'
        });

        await resetPasswordHandler(req, res);

        expect(res.statusCode).toBe(400);
        expect(res._getJSONData()).toEqual({
            message: 'Invalid or expired token'
        });
    });

    it('should clean up expired tokens', async () => {
        // Mock Date.now to test token expiry
        const realDateNow = Date.now;
        const currentTime = Date.now();

        try {
            // Create a token
            const testEmail = 'expiry@example.com';
            Date.now = jest.fn().mockReturnValue(currentTime);

            const { req: req1, res: res1 } = mockRequestResponse('POST', { email: testEmail });
            await resetPasswordHandler(req1, res1);

            expect(res1.statusCode).toBe(200);

            // Fast forward time to make token expire
            Date.now = jest.fn().mockReturnValue(currentTime + (61 * 60 * 1000)); // 61 minutes later

            // Check token validity
            const { req: req2, res: res2 } = mockRequestResponse('GET', {}, {
                email: testEmail,
                token: 'test-token-12345'
            });

            await resetPasswordHandler(req2, res2);

            expect(res2.statusCode).toBe(200);
            expect(res2._getJSONData()).toHaveProperty('valid', false);
        } finally {
            // Restore the real Date.now
            Date.now = realDateNow;
        }
    });
});
