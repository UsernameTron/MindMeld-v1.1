import { describe, it, expect, vi, beforeEach } from 'vitest';
import refreshHandler from '../../auth/refresh';
import { signAccessToken, verifyRefreshToken } from '../../../../utils/jwt';

// Mock JWT utilities
vi.mock('../../../../utils/jwt', () => ({
  signAccessToken: vi.fn(),
  verifyRefreshToken: vi.fn(),
}));

// Replace node-mocks-http with a minimal manual mock for req/res
function createMockReqRes({ method = 'POST', cookies = {}, body = {} } = {}) {
  const req: any = { method, cookies, body };
  let statusCode = 200;
  let jsonData: any = undefined;
  let headers: Record<string, string> = {};
  
  const res: any = {
    status(code: number) {
      statusCode = code;
      return res;
    },
    json(data: any) {
      jsonData = data;
      return res;
    },
    setHeader(name: string, value: string) {
      headers[name] = value;
      return res;
    },
    getHeader(name: string) {
      return headers[name];
    },
    _getStatusCode() {
      return statusCode;
    },
    _getData() {
      return JSON.stringify(jsonData);
    },
    _getHeaders() {
      return headers;
    }
  };
  return { req, res };
}

describe('/api/auth/refresh', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return 401 if no refresh token cookie exists', async () => {
    const { req, res } = createMockReqRes({
      method: 'POST',
      cookies: {},
    });

    await refreshHandler(req, res);

    expect(res._getStatusCode()).toBe(401);
    expect(JSON.parse(res._getData())).toEqual(
      expect.objectContaining({
        error: expect.any(String),
      })
    );
  });

  it('should return 401 if refresh token is invalid', async () => {
    const { req, res } = createMockReqRes({
      method: 'POST',
      cookies: {
        refreshToken: 'invalid-token',
      },
    });

    vi.mocked(verifyRefreshToken).mockReturnValueOnce(null);

    await refreshHandler(req, res);

    expect(res._getStatusCode()).toBe(401);
    expect(verifyRefreshToken).toHaveBeenCalledWith('invalid-token');
  });

  it('should issue new access token if refresh token is valid', async () => {
    const userId = '123';
    const newAccessToken = 'new-access-token';

    const { req, res } = createMockReqRes({
      method: 'POST',
      cookies: {
        refreshToken: 'valid-refresh-token',
      },
    });

    vi.mocked(verifyRefreshToken).mockReturnValueOnce({ userId });
    vi.mocked(signAccessToken).mockReturnValueOnce(newAccessToken);

    await refreshHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(JSON.parse(res._getData())).toEqual({
      access_token: newAccessToken,
    });
    expect(verifyRefreshToken).toHaveBeenCalledWith('valid-refresh-token');
    expect(signAccessToken).toHaveBeenCalledWith({ sub: userId });
    expect(res.getHeader('Set-Cookie')).toBeDefined();
  });
});
