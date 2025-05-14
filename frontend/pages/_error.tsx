import React from 'react';
import { NextPageContext } from 'next';
import { ErrorDisplay } from '../src/components/ui/molecules/ErrorDisplay/ErrorDisplay';
import Head from 'next/head';

interface ErrorPageProps {
  statusCode?: number;
  message?: string;
}

const ErrorPage = ({ statusCode, message }: ErrorPageProps) => {
  const errorMessage = message || 
    statusCode 
      ? `An error ${statusCode} occurred on the server` 
      : 'An error occurred on the client';

  return (
    <>
      <Head>
        <title>Error | MindMeld</title>
      </Head>
      <div className="flex flex-col items-center justify-center min-h-screen w-full bg-red-50 dark:bg-red-900 p-4">
        <ErrorDisplay 
          severity="error" 
          title="Something went wrong" 
          message={errorMessage} 
          code={statusCode?.toString()}
        />
        <div className="mt-6">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => window.location.href = '/'}
          >
            Go to Home
          </button>
        </div>
      </div>
    </>
  );
};

ErrorPage.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  const message = err?.message || undefined;
  return { statusCode, message };
};

export default ErrorPage;