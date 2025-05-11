'use client';
import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ErrorDisplay } from '@/components/ErrorDisplay/ErrorDisplay.tsx';
import { Button } from '@/components/Button.tsx';

export default function AnalyzeError({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  useEffect(() => {
    // Log error to monitoring service
     
    console.error('Analyze page error:', error);
  }, [error]);
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full bg-red-50 dark:bg-red-900">
      <ErrorDisplay severity="error" title="Something went wrong" message={error.message || 'An error occurred.'} />
      <div className="flex gap-4 mt-6">
        <Button variant="primary" onClick={reset} data-testid="retry-btn">Retry</Button>
        <Button variant="secondary" onClick={() => router.push('/dashboard')} data-testid="dashboard-btn">Go to Dashboard</Button>
      </div>
    </div>
  );
}
