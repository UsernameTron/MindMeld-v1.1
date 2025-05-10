import { Page } from '@playwright/test';

/**
 * Mock API responses for E2E tests
 * @param page - Playwright page
 */
export async function mockApiResponses(page: Page): Promise<void> {
  console.log('Setting up API mocks for Playwright tests...');
  
  // Log all requests for debugging
  await page.route('**', async (route, request) => {
    console.log(`Request: ${request.method()} ${request.url()}`);
    // Continue with the request
    await route.continue();
  }, { position: 'first' });
  
  // Mock authentication endpoints
  await page.route('/api/auth/token', async (route) => {
    console.log('Intercepted auth token request');
    const request = route.request();
    if (request.method() === 'POST') {
      const body = JSON.parse(await request.postData() || '{}');
      console.log('Auth request body:', body);
      
      if (body.username === 'test@example.com' && body.password === 'password123') {
        console.log('Sending successful auth response');
        
        // Set the auth cookie directly on the page context with the correct name
        const cookie = {
          name: 'auth_token',  // This must match the name in middleware.ts
          value: 'mock-valid-token',
          path: '/',
          domain: new URL(request.url()).hostname || 'localhost',
          httpOnly: true,
          secure: process.env.NODE_ENV !== 'development',
          sameSite: 'Strict' as const,
          expires: Date.now() / 1000 + 3600
        };
        
        await page.context().addCookies([cookie]);
        console.log('Cookie set directly:', cookie);
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: {
            'Set-Cookie': `auth_token=mock-valid-token; Path=/; HttpOnly; Max-Age=3600; SameSite=Strict`
          },
          body: JSON.stringify({
            access_token: 'mock-valid-token',
            token_type: 'bearer',
            expires_in: 3600
          })
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Invalid credentials' })
        });
      }
    }
  });

  // Mock token refresh
  await page.route('/api/auth/refresh', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-refreshed-token',
        token_type: 'bearer',
        expires_in: 3600
      })
    });
  });

  // Mock token validation
  await page.route('/api/auth/validate', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ valid: true })
    });
  });

  // Mock logout endpoint
  await page.route('/api/auth/logout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true })
    });
  });

  // Mock dashboard API data
  await page.route('/api/data', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ value: 'Hello from the API!' })
    });
  });
  
  // Handle all API routes that aren't explicitly mocked
  await page.route('/api/**', async (route) => {
    if (!route.request().url().includes('/auth/') && !route.request().url().includes('/data')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    }
  });
}
