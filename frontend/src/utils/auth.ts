import { GetServerSidePropsContext, GetServerSidePropsResult } from 'next';
import { routeRequiresAuth } from '../config/routes';
import { verifyToken } from './jwt';

/**
 * Higher-order function to wrap getServerSideProps with authentication check
 * Use this to protect server-side rendered pages
 */
export function withAuthSSR<P extends { [key: string]: any } = { [key: string]: any }>(
  getServerSideProps?: (context: GetServerSidePropsContext) => Promise<GetServerSidePropsResult<P>>
) {
  return async (context: GetServerSidePropsContext): Promise<GetServerSidePropsResult<P>> => {
    const { req, res } = context;
    
    // Get auth token from cookies
    const authToken = req.cookies.auth_token;
    
    if (!authToken) {
      console.log('[withAuthSSR] No auth_token cookie found, redirecting to login');
      // Redirect to login with return URL
      return {
        redirect: {
          destination: `/login?returnTo=${encodeURIComponent(context.resolvedUrl)}`,
          permanent: false,
        },
      };
    }
    
    // Verify token
    try {
      const payload = verifyToken(authToken);
      
      if (!payload) {
        console.log('[withAuthSSR] Invalid or expired token, redirecting to login');
        return {
          redirect: {
            destination: `/login?returnTo=${encodeURIComponent(context.resolvedUrl)}`,
            permanent: false,
          },
        };
      }
      
      console.log('[withAuthSSR] Token valid for user:', payload.email);
      
      // If the user provided a getServerSideProps function, call it
      if (getServerSideProps) {
        return await getServerSideProps(context);
      }
      
      // Otherwise, just return empty props
      return { props: {} as P };
    } catch (error) {
      console.error('[withAuthSSR] Error verifying token:', error);
      return {
        redirect: {
          destination: `/login?returnTo=${encodeURIComponent(context.resolvedUrl)}`,
          permanent: false,
        },
      };
    }
  };
}
