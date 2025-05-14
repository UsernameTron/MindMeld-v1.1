import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/dashboard');
  }, [router]);

  return (
    <>
      <Head>
        <title>MindMeld</title>
        <meta name="description" content="Your coding assistant dashboard" />
      </Head>
      <div className="flex items-center justify-center min-h-screen">
        {/* Optional loading indicator */}
        <div className="animate-pulse">Redirecting...</div>
      </div>
    </>
  );
}