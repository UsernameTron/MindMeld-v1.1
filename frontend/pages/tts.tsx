import React from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import { ErrorBoundary } from '../src/components/common/ErrorBoundary';
import { ErrorDisplay } from '../src/components/ui/molecules/ErrorDisplay/ErrorDisplay';
import { DashboardLayout } from '../src/components/layout/DashboardLayout';
import { RequireAuth } from '../src/components/auth/RequireAuth';
import { withAuthSSR } from '../src/utils/auth';

const TTSPlayer = dynamic(() => import('../src/components/ui/organisms/TTSPlayer/TTSPlayer'), { ssr: false });

export const getServerSideProps = withAuthSSR();

export default function TTSPage() {
  return (
    <RequireAuth>
      <Head>
        <title>Text to Speech | MindMeld</title>
        <meta name="description" content="Convert text to natural-sounding speech using advanced AI models." />
      </Head>
      <DashboardLayout>
        <ErrorBoundary 
          category={undefined} 
          fallback={<ErrorDisplay severity="error" message="Something went wrong with the text-to-speech feature" title="TTS Error" />}
        >
          <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Text to Speech</h1>
            <p className="mb-4">Convert text to natural-sounding speech using advanced AI models.</p>
            <TTSPlayer />
          </div>
        </ErrorBoundary>
      </DashboardLayout>
    </RequireAuth>
  );
}