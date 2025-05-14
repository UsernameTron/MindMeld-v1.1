import React, { useState } from 'react';
import UrlInputForm from '@components/forms/UrlInputForm';
import { useSentimentAnalysis } from '@services/sentimentAnalysisService';
import SentimentVisualization, { SentimentData } from '@components/ui/organisms/SentimentVisualization/SentimentVisualization';
import { LoadingIndicator } from '@components/ui/molecules/LoadingIndicator';
import { ErrorDisplay } from '@components/ui/molecules/ErrorDisplay';

// Helper to summarize key emotions
function summarizeEmotions(emotions?: Record<string, number> | null) {
  if (!emotions) return '';
  const sorted = Object.entries(emotions)
    .filter(([_, v]) => v > 0.05)
    .sort((a, b) => b[1] - a[1]);
  if (!sorted.length) return 'No strong emotions detected.';
  return sorted
    .map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)} (${(v * 100).toFixed(0)}%)`)
    .join(', ');
}

export const SentimentSummaryDisplay: React.FC = () => {
  const [history, setHistory] = useState<Array<{
    url: string;
    result?: string;
    error?: string;
    emotions?: Record<string, number>;
    sentiment?: string;
    sentimentScore?: number;
  }>>([]);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [analysis, setAnalysis] = useState<null | {
    emotions: Record<string, number>;
    sentiment: string;
    sentimentScore: number;
  }>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Move the hook call to the top level
  const { analyze } = useSentimentAnalysis();
  
  // Handler for UrlInputForm submission
  const handleUrlSubmit = async (url: string) => {
    setCurrentUrl(url);
    setLoading(true);
    setError(null);
    setAnalysis(null);
    try {
      const data = await analyze(url);
      setAnalysis({
        emotions: data.emotions,
        sentiment: data.overall_sentiment,
        sentimentScore: data.sentiment_score,
      });
      setHistory([{ url, result: data.overall_sentiment, emotions: data.emotions, sentiment: data.overall_sentiment, sentimentScore: data.sentiment_score }, ...history]);
    } catch (err: any) {
      setError(err?.message || 'Analysis failed');
      setHistory([{ url, error: err?.message || 'Analysis failed' }, ...history]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="w-full max-w-3xl mx-auto p-4 flex flex-col gap-6 bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <h1 className="text-2xl font-bold mb-2">Sentiment Analysis Summary</h1>
      {/* URL Input Form */}
      <div>
        <UrlInputForm onSubmit={handleUrlSubmit} loading={loading} />
      </div>
      {/* Loading/Error State */}
      {loading && (
        <div className="flex justify-center my-4"><LoadingIndicator size="md" ariaLabel="Analyzing..." /></div>
      )}
      {error && (
        <ErrorDisplay title="Analysis Error" message={error} severity="error" />
      )}
      {/* Visualization and Summary */}
      {analysis && !loading && !error && (
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="flex-1 min-w-[300px]">
            <SentimentVisualization
              data={{
                overall: { 
                  label: analysis.sentiment.charAt(0).toUpperCase() + analysis.sentiment.slice(1), 
                  value: analysis.sentimentScore
                },
                scores: [
                  { label: 'Positive', value: analysis.sentiment === 'positive' ? analysis.sentimentScore : 0 },
                  { label: 'Negative', value: analysis.sentiment === 'negative' ? analysis.sentimentScore : 0 },
                  { label: 'Neutral', value: analysis.sentiment === 'neutral' ? analysis.sentimentScore : 0 }
                ]
              }}
            />
          </div>
          <div className="flex-1 min-w-[220px]">
            <div className="p-4 rounded bg-blue-50 border border-blue-200 text-blue-900 dark:bg-blue-900 dark:text-blue-100 dark:border-blue-700">
              <h2 className="text-lg font-semibold mb-2">Summary</h2>
              <div className="mb-1"><span className="font-medium">Overall Sentiment:</span> {analysis.sentiment.charAt(0).toUpperCase() + analysis.sentiment.slice(1)}</div>
              <div className="mb-1"><span className="font-medium">Sentiment Score:</span> {(analysis.sentimentScore * 100).toFixed(1)}%</div>
              <div><span className="font-medium">Key Emotions:</span> {summarizeEmotions(analysis.emotions)}</div>
            </div>
          </div>
        </div>
      )}
      {/* History */}
      {history.length > 0 && (
        <div className="mt-6">
          <h2 className="text-base font-semibold mb-2">Analysis History</h2>
          <ul className="space-y-1">
            {history.map((item, idx) => (
              <li key={idx} className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-xs">
                <span className="truncate max-w-xs" title={item.url}>{item.url}</span>
                {item.result && (
                  <span className="text-green-700">Result: {item.result}</span>
                )}
                {item.error && (
                  <span className="text-red-600">Error: {item.error}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
};

export default SentimentSummaryDisplay;
