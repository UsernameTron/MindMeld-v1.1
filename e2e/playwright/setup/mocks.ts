import { Page } from '@playwright/test';

interface MockOptions {
  tokenExpiresIn?: number; // Token expiry in seconds
}

/**
 * Mock API responses for E2E tests
 * @param page - Playwright page
 * @param options - Options for mock behavior
 */
export async function mockApiResponses(page: Page, options: MockOptions = {}): Promise<void> {
  console.log('Setting up API mocks for Playwright tests...');
  
  // Default token expiry to 1 hour (3600 seconds)
  const tokenExpiresIn = options.tokenExpiresIn || 3600;
  
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
      
      if (body.email && body.password) {
        console.log('Sending successful auth response');
        
        // Set cookies directly
        const cookies = [
          {
            name: 'auth_token',
            value: 'mock-valid-token',
            path: '/',
            domain: new URL(request.url()).hostname || 'localhost',
            httpOnly: true,
            secure: false,
            sameSite: 'Strict' as const,
            expires: Date.now() / 1000 + tokenExpiresIn
          },
          {
            name: 'refresh_token',
            value: 'mock-valid-refresh-token',
            path: '/',
            domain: new URL(request.url()).hostname || 'localhost',
            httpOnly: true,
            secure: false,
            sameSite: 'Strict' as const,
            expires: Date.now() / 1000 + (tokenExpiresIn * 7) // 7 days
          }
        ];
        
        await page.context().addCookies(cookies);
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Authenticated successfully',
            user: {
              id: 'test-user-id',
              name: 'Test User',
              email: body.email
            }
          })
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Invalid credentials' })
        });
      }
    } else {
      await route.continue();
    }
  });

  // Mock user profile endpoint
  await page.route('/api/auth/user', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'test-user-id',
        name: 'Test User',
        email: 'test@example.com'
      })
    });
  });

  // Mock token refresh
  await page.route('/api/auth/refresh', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'mock-refreshed-token'
        })
      });
      
      // Update the auth cookie
      await page.context().addCookies([
        {
          name: 'auth_token',
          value: 'mock-refreshed-token',
          path: '/',
          domain: new URL(route.request().url()).hostname || 'localhost',
          httpOnly: true,
          secure: false,
          sameSite: 'Strict' as const,
          expires: Date.now() / 1000 + tokenExpiresIn
        }
      ]);
    } else {
      await route.continue();
    }
  });

  // Mock token validation
  await page.route('/api/auth/validate', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ 
        valid: true,
        message: 'Session is valid',
        user: {
          userId: 'test-user-id',
          email: 'test@example.com'
        }
      })
    });
  });

  // Mock logout endpoint
  await page.route('/api/auth/logout', async (route) => {
    if (route.request().method() === 'POST') {
      // Clear the cookies
      await page.context().clearCookies();
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Logged out successfully' })
      });
    } else {
      await route.continue();
    }
  });

  // Mock LibreChat proxy endpoint
  await page.route('/api/proxy/librechat/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        models: [
          { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
          { id: 'gpt-4', name: 'GPT-4' }
        ],
        message: 'Proxy request successful'
      })
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
    const url = route.request().url();
    if (!url.includes('/auth/') && 
        !url.includes('/data') &&
        !url.includes('/proxy/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    } else {
      await route.continue();
    }
  });
}