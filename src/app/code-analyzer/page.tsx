import React, { Suspense } from 'react';
import dynamic from 'next/dynamic';

const CodeAnalyzer = dynamic(
  () => import('../../components/organisms/CodeAnalyzer/CodeAnalyzer'),
  { ssr: false, loading: () => <div role="status" aria-busy="true">Loading Code Analyzer...</div> }
);

const CodeAnalyzerPage = () => (
  <main className="code-analyzer-page" aria-label="Code Analyzer Page">
    <h1>Code Analyzer</h1>
    <Suspense fallback={<div role="status" aria-busy="true">Loading...</div>}>
      <CodeAnalyzer />
    </Suspense>
  </main>
);

export default CodeAnalyzerPage;
