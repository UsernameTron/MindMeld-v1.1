import React from 'react';
import { LoadingIndicator } from '@/components/LoadingIndicator/LoadingIndicator.tsx';

export default function AnalyzeLoading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full bg-slate-50 dark:bg-slate-900">
      <LoadingIndicator variant="spinner" size="lg" />
      <div className="mt-4 text-slate-500 text-lg">Loading Code Analyzer...</div>
    </div>
  );
}
