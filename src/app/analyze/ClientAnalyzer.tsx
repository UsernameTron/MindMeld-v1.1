'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { LoadingIndicator } from '@/components/ui/LoadingIndicator';

// Dynamic import for CodeAnalyzer
const CodeAnalyzer = dynamic(
  () => import('@/components/CodeAnalyzer/CodeAnalyzer').then(mod => mod.default),
  { ssr: false, loading: () => <LoadingIndicator size={24} /> }
);

const ClientAnalyzer: React.FC = () => {
  return (
    <div className="w-full h-full">
      <CodeAnalyzer />
    </div>
  );
};

export default ClientAnalyzer;
