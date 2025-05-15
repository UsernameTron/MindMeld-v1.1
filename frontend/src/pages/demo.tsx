import React, { useState } from 'react';
import { LoadingIndicator } from '../components/molecules/LoadingIndicator';
import { ErrorDisplay } from '../components/molecules/ErrorDisplay';
import { FeatureErrorBoundary } from '../components/organisms/ErrorBoundary/FeatureErrorBoundary';

export default function DemoPage() {
  const [showError, setShowError] = useState(false);
  const [loading, setLoading] = useState(false);

  return (
    <div className="max-w-xl mx-auto py-10 space-y-8">
      <h1 className="text-2xl font-bold mb-4">Component Demo</h1>
      <section>
        <h2 className="font-semibold mb-2">LoadingIndicator</h2>
        <div className="flex gap-4 items-center">
          <LoadingIndicator size="sm" ariaLabel="Loading small" />
          <LoadingIndicator size="md" ariaLabel="Loading medium" />
          <LoadingIndicator size="lg" ariaLabel="Loading large" />
        </div>
      </section>
      <section>
        <h2 className="font-semibold mb-2">ErrorDisplay</h2>
        <ErrorDisplay message="This is an error." severity="error" title="Error" code="ERR_1" onRetry={() => alert('Retry!')} />
        <ErrorDisplay message="This is a warning." severity="warning" title="Warning" dismissible onDismiss={() => alert('Dismissed!')} />
        <ErrorDisplay message="This is info." severity="info" title="Info" />
      </section>
      <section>
        <h2 className="font-semibold mb-2">FeatureErrorBoundary</h2>
        <button className="mb-2 px-3 py-1 bg-blue-600 text-white rounded" onClick={() => setShowError(true)}>
          Trigger Error
        </button>
        <FeatureErrorBoundary name="Demo Feature">
          {showError ? (() => { throw new Error('Demo error!'); })() : <div>No error yet.</div>}
        </FeatureErrorBoundary>
      </section>
      <section>
        <h2 className="font-semibold mb-2">Loading + Error Integration</h2>
        <button
          className="px-3 py-1 bg-green-600 text-white rounded mr-2"
          onClick={() => {
            setLoading(true);
            setTimeout(() => setLoading(false), 2000);
          }}
        >
          Simulate Loading
        </button>
        {loading && <LoadingIndicator size="md" />}
      </section>
    </div>
  );
}
