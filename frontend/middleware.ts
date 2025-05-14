import { NextResponse } from '@/shims/server';
import type { NextRequest } from '@/shims/server';

export function middleware(request: NextRequest) {
  // Get the pathname of the request
  const { pathname } = request.nextUrl;

  // Allowed public paths that don't require authentication
  const isPublicPath = 
    pathname === '/login' || 
    pathname.startsWith('/api/auth/token') || 
    pathname.startsWith('/api/auth/refresh') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.startsWith('/images') ||
    pathname === '/favicon.ico';

  // Check if user has auth token
  const authToken = request.cookies.get('auth_token')?.value;
  
  // API routes except auth routes should return 401 instead of redirect
  const isApiRoute = pathname.startsWith('/api/') && !pathname.startsWith('/api/auth/');
  
  // Handle protected routes
  if (!isPublicPath && !authToken) {
    if (isApiRoute) {
      // Return 401 for API routes
      return new NextResponse(
        JSON.stringify({ message: 'Authentication required' }),
        { 
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      // Redirect to login page for regular routes
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Handle login page when user is already authenticated
  if (pathname === '/login' && authToken) {
    // User already logged in but trying to access login page, redirect to dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // For secure cookie transmission
  const response = NextResponse.next();
  
  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  return response;
}

export const config = {
  // Matcher ignoring /_next/static, /favicon.ico, etc
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
