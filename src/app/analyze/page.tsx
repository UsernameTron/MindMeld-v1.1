import React from 'react';
import { Metadata } from 'next';
import ClientAnalyzer from './ClientAnalyzer';

export const metadata: Metadata = {
  title: 'Code Analyzer | MindMeld',
  description: 'Analyze your code for errors, get suggestions, and improve your development workflow',
};

// This is a Server Component
export default function AnalyzePage() {
  return (
    <div className="container mx-auto p-4 pb-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Code Analyzer</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Analyze your code for errors, get suggestions, and improve your development workflow
        </p>
      </div>
      <ClientAnalyzer />
    </div>
  );
}
