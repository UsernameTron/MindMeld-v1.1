import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

const NotFoundPage: React.FC = () => {
  return (
    <>
      <Head>
        <title>404 - Page Not Found | MindMeld</title>
        <meta name="description" content="The page you were looking for couldn't be found." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <div className="w-full max-w-md text-center">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-2">404</h1>
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-200 mb-4">Page Not Found</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
              Go to Home
            </Link>
            <Link href="/dashboard" className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition">
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default NotFoundPage;
