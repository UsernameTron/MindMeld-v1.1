'use client';

// Import from next.js
import { Suspense } from 'react';
import Loading from './loading';

// Direct import instead of using dynamic import to avoid type issues
import CodeAnalyzer from '@/components/CodeAnalyzer/CodeAnalyzer';

export default function ClientAnalyzer() {
  return (
    <Suspense fallback={<Loading />}>
      <CodeAnalyzer />
    </Suspense>
  );
}
