import { NextApiRequest, NextApiResponse } from 'next';
import { createMocks } from 'node-mocks-http';
import loginAttemptHandler from '../../pages/api/auth/loginAttempt';

// Mock the loginAttempts in-memory store
const originalLoginAttempts = {};
let mockLoginAttempts = {};

// Helper to create mocked request/response
const mockRequestResponse = (method = 'POST', body = {}) => {
    const { req, res } = createMocks({
        method,
        body,
    });
    return { req: req as NextApiRequest, res: res as NextApiResponse };
};

describe('Login Attempt Handler', () => {
    beforeEach(() => {
        // Reset the mock login attempts before each test
        mockLoginAttempts = {};
        // Mock the login attempts storage
        jest.mock('../../pages/api/auth/loginAttempt', () => {
            const originalModule = jest.requireActual('../../pages/api/auth/loginAttempt');
            const handler = originalModule.default;

            // Replace the handler with our own implementation
            return {
                __esModule: true,
                default: (req, res) => {
                    return handler(req, res);
                },
                loginAttempts: mockLoginAttempts,
            };
        });
    });

    it('should reject requests with invalid methods', async () => {
        const { req, res } = mockRequestResponse('GET');

        await loginAttemptHandler(req, res);

        expect(res.statusCode).toBe(405);
        expect(res._getJSONData()).toEqual({
            message: 'Method not allowed'
        });
    });

    it('should require email parameter', async () => {
        const { req, res } = mockRequestResponse('POST', { action: 'check' });

        await loginAttemptHandler(req, res);

        expect(res.statusCode).toBe(400);
        expect(res._getJSONData()).toEqual({
            message: 'Email parameter is required'
        });
    });

    it('should initialize a new record for first check', async () => {
        const testEmail = 'newuser@example.com';
        const { req, res } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'check'
        });

        await loginAttemptHandler(req, res);

        expect(res.statusCode).toBe(200);
        expect(res._getJSONData()).toHaveProperty('attempts', 0);
        expect(res._getJSONData()).toHaveProperty('locked', false);
        expect(res._getJSONData()).toHaveProperty('remainingAttempts', 5);
    });

    it('should increment failed attempts', async () => {
        const testEmail = 'failinguser@example.com';

        // First failed attempt
        const { req: req1, res: res1 } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'failure'
        });

        await loginAttemptHandler(req1, res1);

        expect(res1.statusCode).toBe(200);
        expect(res1._getJSONData()).toHaveProperty('attempts', 1);
        expect(res1._getJSONData()).toHaveProperty('remainingAttempts', 4);

        // Second failed attempt
        const { req: req2, res: res2 } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'failure'
        });

        await loginAttemptHandler(req2, res2);

        expect(res2.statusCode).toBe(200);
        expect(res2._getJSONData()).toHaveProperty('attempts', 2);
        expect(res2._getJSONData()).toHaveProperty('remainingAttempts', 3);
    });

    it('should lock account after max attempts', async () => {
        const testEmail = 'lockeduser@example.com';

        // Simulate 5 failed attempts
        for (let i = 0; i < 5; i++) {
            const { req, res } = mockRequestResponse('POST', {
                email: testEmail,
                action: 'failure'
            });

            await loginAttemptHandler(req, res);

            // If this is the 5th attempt, account should be locked
            if (i === 4) {
                expect(res.statusCode).toBe(403);
                expect(res._getJSONData()).toHaveProperty('locked', true);
                expect(res._getJSONData()).toHaveProperty('message', expect.stringContaining('Account is locked'));
            } else {
                expect(res.statusCode).toBe(200);
            }
        }

        // Try checking after lockout
        const { req: checkReq, res: checkRes } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'check'
        });

        await loginAttemptHandler(checkReq, checkRes);

        expect(checkRes.statusCode).toBe(403);
        expect(checkRes._getJSONData()).toHaveProperty('locked', true);
        expect(checkRes._getJSONData()).toHaveProperty('remainingLockoutTime');
    });

    it('should reset attempts on successful login', async () => {
        const testEmail = 'successuser@example.com';

        // First register a failed attempt
        const { req: failReq, res: failRes } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'failure'
        });

        await loginAttemptHandler(failReq, failRes);

        // Then register a successful login
        const { req: successReq, res: successRes } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'success'
        });

        await loginAttemptHandler(successReq, successRes);

        expect(successRes.statusCode).toBe(200);

        // Check that attempts were reset
        const { req: checkReq, res: checkRes } = mockRequestResponse('POST', {
            email: testEmail,
            action: 'check'
        });

        await loginAttemptHandler(checkReq, checkRes);

        expect(checkRes.statusCode).toBe(200);
        expect(checkRes._getJSONData()).toHaveProperty('attempts', 0);
        expect(checkRes._getJSONData()).toHaveProperty('locked', false);
    });
});
