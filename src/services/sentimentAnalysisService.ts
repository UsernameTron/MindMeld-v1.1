// src/services/sentimentAnalysisService.ts
// Frontend service for web sentiment analysis API

export interface SentimentResponse {
  overall_sentiment: 'positive' | 'negative' | 'neutral';
  sentiment_score: number;
  subjectivity: number;
  emotions: {
    joy: number;
    anger: number;
    fear: number;
    sadness: number;
    surprise: number;
    disgust: number;
    [key: string]: number;
  };
  confidence: number;
}

export interface SentimentRequest {
  url: string;
}

export interface SentimentAnalysisState {
  loading: boolean;
  error: string | null;
  data: SentimentResponse | null;
}

// Simple in-memory cache for analyzed URLs
const sentimentCache = new Map<string, SentimentResponse>();

/**
 * Analyze sentiment for a given URL using the backend API.
 * Handles loading, error, and caching states.
 * @param url The URL to analyze
 * @param options Optional: { retry: number } for retry attempts
 */
export async function analyzeSentiment(
  url: string,
  options?: { retry?: number }
): Promise<SentimentResponse> {
  if (sentimentCache.has(url)) {
    return sentimentCache.get(url)!;
  }
  let lastError: any = null;
  const maxRetries = options?.retry ?? 1;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const res = await fetch('/api/v1/sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `API error: ${res.status}`);
      }
      const data: SentimentResponse = await res.json();
      sentimentCache.set(url, data);
      return data;
    } catch (err: any) {
      lastError = err;
      if (attempt < maxRetries - 1) {
        await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
      }
    }
  }
  throw lastError || new Error('Unknown error');
}

/**
 * React hook for sentiment analysis with loading/error state.
 * Usage:
 *   const { data, loading, error, analyze } = useSentimentAnalysis();
 */
import { useState, useCallback } from 'react';

export function useSentimentAnalysis() {
  const [state, setState] = useState<SentimentAnalysisState>({
    loading: false,
    error: null,
    data: null,
  });

  const analyze = useCallback(async (url: string, opts?: { retry?: number }) => {
    setState({ loading: true, error: null, data: null });
    try {
      const data = await analyzeSentiment(url, opts);
      setState({ loading: false, error: null, data });
      return data;
    } catch (error: any) {
      setState({ loading: false, error: error.message || 'Unknown error', data: null });
      throw error;
    }
  }, []);

  return { ...state, analyze };
}

// Example usage:
// const { data, loading, error, analyze } = useSentimentAnalysis();
// useEffect(() => { analyze('https://example.com'); }, []);
