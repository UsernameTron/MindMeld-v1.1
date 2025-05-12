import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';
import { resetRouterMocks } from '../src/__mocks__/next/router.js';
import { resetAuthServiceMocks } from '../src/__mocks__/services/authService.js';
import { resetJwtMocks } from '../src/__mocks__/utils/jwt.js';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

beforeEach(() => {
  vi.clearAllMocks();
  document.cookie = '';
  localStorage.clear();
  resetRouterMocks();
  resetAuthServiceMocks();
  resetJwtMocks();
});

// Global test setup code here
