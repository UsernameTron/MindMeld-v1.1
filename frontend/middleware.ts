import { NextResponse } from '@/shims/server';
import type { NextRequest } from '@/shims/server';

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  // Get the pathname of the request
  const { pathname } = request.nextUrl;

  // Allowed public paths that don't require authentication
  const isPublicPath = 
    pathname === '/login' || 
    pathname === '/api/auth/token' || 
    pathname === '/api/auth/refresh';

  // Check if user has auth token
  const authToken = request.cookies.get('auth_token')?.value;

  // Handle protected routes
  if (!isPublicPath && !authToken) {
    // User trying to access protected route without token, redirect to login
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Handle login page when user is already authenticated
  if (pathname === '/login' && authToken) {
    // User already logged in but trying to access login page, redirect to dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Matcher ignoring /_next/static, /favicon.ico, etc
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
