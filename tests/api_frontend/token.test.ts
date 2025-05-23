import { NextApiRequest, NextApiResponse } from 'next';
import { createMocks } from 'node-mocks-http';
import tokenHandler from '../../pages/api/auth/token';
import fetch from 'node-fetch';

// Add extended type definitions
interface MockResponse extends NextApiResponse {
    _getJSONData(): any;
    _getData(): string;
    _getStatusCode(): number;
    _isEndCalled(): boolean;
    getHeader(name: string): string | string[] | number | undefined;
}

// Mock the node-fetch module
jest.mock('node-fetch', () => jest.fn());
const mockedFetch = jest.fn();

// Mock the JWT utils
jest.mock('../../src/utils/jwt', () => ({
    generateAccessToken: jest.fn(() => 'test-access-token'),
    generateRefreshToken: jest.fn(() => 'test-refresh-token')
}));

// Helper to create mocked request/response
const mockRequestResponse = (method = 'POST', body = {}) => {
    const { req, res } = createMocks({
        method: method as any, // Type assertion to resolve RequestMethod issue
        body,
    });
    return { req: req as NextApiRequest, res: res as MockResponse };
};

describe('Token Authentication Handler', () => {
    beforeEach(() => {
        // Reset module cache and mock implementations
        jest.resetModules();
        jest.clearAllMocks();
        Object.defineProperty(process.env, 'NODE_ENV', {
            value: 'development',
            configurable: true
        });

        // Default fetch mock implementation for checking login attempts
        mockedFetch.mockImplementation(async () => ({
            ok: true,
            json: async () => ({ locked: false }),
            // Add other properties as needed
        } as Response));
    });

    it('should handle OPTIONS requests for CORS', async () => {
        const { req, res } = mockRequestResponse('OPTIONS');

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(200);
        expect(res._getData()).toBe(''); // Empty response
    });

    it('should reject non-POST methods', async () => {
        const { req, res } = mockRequestResponse('GET');

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(405);
        expect(res._getJSONData()).toEqual({
            message: 'Method not allowed'
        });
    });

    it('should require email and password', async () => {
        const { req: reqNoEmail, res: resNoEmail } = mockRequestResponse('POST', { password: 'test123' });

        await tokenHandler(reqNoEmail, resNoEmail);

        expect(resNoEmail.statusCode).toBe(400);
        expect(resNoEmail._getJSONData()).toEqual({
            message: 'Email and password are required'
        });

        const { req: reqNoPass, res: resNoPass } = mockRequestResponse('POST', { email: 'test@example.com' });

        await tokenHandler(reqNoPass, resNoPass);

        expect(resNoPass.statusCode).toBe(400);
        expect(resNoPass._getJSONData()).toEqual({
            message: 'Email and password are required'
        });
    });

    it('should check if account is locked', async () => {
        // Mock locked account response
        mockedFetch.mockImplementationOnce(async () => ({
            json: async () => ({
                locked: true,
                remainingLockoutTime: 14
            }),
        } as Response));

        const { req, res } = mockRequestResponse('POST', {
            email: 'locked@example.com',
            password: 'password123'
        });

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(403);
        expect(res._getJSONData()).toHaveProperty('locked', true);
        expect(res._getJSONData()).toHaveProperty('message', expect.stringContaining('Account is locked'));
        expect(res._getJSONData()).toHaveProperty('remainingLockoutTime', 14);
    });

    it('should authenticate test user successfully', async () => {
        // Mock successful login attempt record
        mockedFetch.mockImplementation(async () => {
            return {
                json: async () => ({}),
            } as Response;
        });

        const { req, res } = mockRequestResponse('POST', {
            email: 'test@example.com',
            password: 'Test123!'
        });

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(200);
        expect(res._getJSONData()).toHaveProperty('message', 'Authentication successful');
        expect(res._getJSONData()).toHaveProperty('user.id', 'test-user-1');
        expect(res._getJSONData()).toHaveProperty('user.name', 'Test User');

        // Check cookies
        const cookies = res.getHeader('Set-Cookie') as string[];
        expect(cookies).toHaveLength(2);
        expect(cookies[0]).toContain('auth_token=test-access-token');
        expect(cookies[1]).toContain('refresh_token=test-refresh-token');
    });

    it('should set secure cookies in production mode', async () => {
        // Store original NODE_ENV
        const originalNodeEnv = process.env.NODE_ENV;
        // Set env to production using Object.defineProperty
        Object.defineProperty(process.env, 'NODE_ENV', {
            value: 'production',
            configurable: true
        });

        const { req, res } = mockRequestResponse('POST', {
            email: 'test@example.com',
            password: 'Test123!'
        });

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(200);

        const cookies = res.getHeader('Set-Cookie') as string[];
        expect(cookies[0]).toContain('Secure');
        expect(cookies[1]).toContain('Secure');

        // Restore original NODE_ENV
        Object.defineProperty(process.env, 'NODE_ENV', {
            value: originalNodeEnv,
            configurable: true
        });
    });

    it('should record failed login attempt', async () => {
        // Mock failure response
        let calledWithFailure = false;
        mockedFetch.mockImplementation(async (url, options) => {
            const body = options?.body ? JSON.parse(options.body as string) : {};

            if (body.action === 'failure') {
                calledWithFailure = true;
                return {
                    json: async () => ({
                        locked: false,
                        remainingAttempts: 4,
                        message: 'Failed login attempt 1/5'
                    }),
                } as Response;
            }

            return {
                json: async () => ({ locked: false }),
            } as Response;
        });

        const { req, res } = mockRequestResponse('POST', {
            email: 'test@example.com',
            password: 'WrongPassword'
        });

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(401);
        expect(calledWithFailure).toBe(true);
        expect(res._getJSONData()).toHaveProperty('message',
            expect.stringContaining('Invalid email or password. 4 login attempts remaining'));
        expect(res._getJSONData()).toHaveProperty('remainingAttempts', 4);
    });

    it('should lock account on too many failed attempts', async () => {
        // Mock account lockout after failure
        mockedFetch.mockImplementationOnce(async () => {
            return {
                json: async () => ({ locked: false }),
            } as Response;
        }).mockImplementationOnce(async () => {
            return {
                json: async () => ({
                    locked: true,
                    message: 'Too many failed login attempts. Account is locked for 15 minutes.',
                    remainingLockoutTime: 15
                }),
            } as Response;
        });

        const { req, res } = mockRequestResponse('POST', {
            email: 'test@example.com',
            password: 'WrongPassword'
        });

        await tokenHandler(req, res);

        expect(res.statusCode).toBe(403);
        expect(res._getJSONData()).toHaveProperty('locked', true);
        expect(res._getJSONData()).toHaveProperty('message',
            expect.stringContaining('Too many failed login attempts'));
    });

    it('should handle API errors gracefully', async () => {
        // Mock fetch to throw error
        mockedFetch.mockImplementation(() => {
            throw new Error('Network error');
        });

        const { req, res } = mockRequestResponse('POST', {
            email: 'test@example.com',
            password: 'Test123!'
        });

        await tokenHandler(req, res);

        // Should still proceed with login despite lockout check error
        expect(res.statusCode).toBe(200);
        expect(res._getJSONData()).toHaveProperty('message', 'Authentication successful');
    });
});
