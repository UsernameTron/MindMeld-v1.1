import React from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';

// Use dynamic import with proper path alias
const SentimentSummaryDisplay = dynamic(
  () => import('@components/ui/organisms/SentimentSummaryDisplay/SentimentSummaryDisplay').then(mod => mod.default),
  { ssr: false }
);

// If you have an Auth context/provider, import and use it here
// import { useAuth } from '../path/to/auth';

const SentimentAnalysisPage: React.FC = () => {
  // Example: If authentication is required, redirect or show login
  // const { isAuthenticated } = useAuth();
  // if (!isAuthenticated) return <LoginPrompt />;

  return (
    <>
      <Head>
        <title>Sentiment Analysis | MindMeld</title>
        <meta name="description" content="Analyze the sentiment and emotions of any website with MindMeld's advanced sentiment analysis tool." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta property="og:title" content="Sentiment Analysis | MindMeld" />
        <meta property="og:description" content="Analyze the sentiment and emotions of any website with MindMeld's advanced sentiment analysis tool." />
      </Head>
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
        <header className="w-full bg-white dark:bg-gray-800 shadow px-4 py-4 flex items-center justify-between">
          <nav className="flex gap-6 items-center">
            <a href="/" className="text-xl font-bold text-blue-700 dark:text-blue-300">MindMeld</a>
            <a href="/dashboard" className="text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400">Dashboard</a>
            <a href="/sentiment-analysis" className="text-blue-600 dark:text-blue-400 font-semibold underline">Sentiment Analysis</a>
            {/* Add other nav links as needed */}
          </nav>
        </header>
        <section className="flex-1 flex flex-col items-center justify-start py-8 px-2">
          <SentimentSummaryDisplay />
        </section>
      </main>
    </>
  );
};

export default SentimentAnalysisPage;
