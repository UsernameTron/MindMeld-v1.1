import { GetServerSidePropsContext } from 'next';
import { routeRequiresAuth } from '../config/routes';

export const withAuthSSR = (getServerSideProps?: any) => {
  return async (context: GetServerSidePropsContext) => {
    const { req, resolvedUrl } = context;
    // Check if user is authenticated by verifying cookies
    const authCookie = req.cookies.auth;
    const isAuthenticated = !!authCookie;
    // Check if this route requires authentication
    if (routeRequiresAuth(resolvedUrl) && !isAuthenticated) {
      return {
        redirect: {
          destination: `/login?returnTo=${encodeURIComponent(resolvedUrl)}`,
          permanent: false,
        },
      };
    }
    // Call the original getServerSideProps if it exists
    if (getServerSideProps) {
      return await getServerSideProps(context);
    }
    return { props: {} };
  };
};
