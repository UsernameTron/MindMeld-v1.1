import { NextApiRequest, NextApiResponse } from 'next';

// Mock positive and negative phrases to use for basic sentiment detection
const POSITIVE_PHRASES = ['great', 'good', 'excellent', 'wonderful', 'amazing', 'happy', 'joy', 'love', 'best', 'success'];
const NEGATIVE_PHRASES = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'hate', 'worst', 'failure', 'poor', 'disaster'];

interface SentimentResponse {
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
  url: string;
}

/**
 * Simple sentiment analysis API endpoint
 * This is a mock implementation that returns sample data
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { url } = req.body;

    if (!url || typeof url !== 'string') {
      return res.status(400).json({ message: 'URL is required' });
    }

    // Check if valid URL
    try {
      new URL(url);
    } catch (e) {
      return res.status(400).json({ message: 'Invalid URL format' });
    }

    // For demo purposes, simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Generate consistent but pseudo-random sentiment based on URL
    // This ensures same URL always returns same result
    const urlSum = Array.from(url).reduce((sum, char) => sum + char.charCodeAt(0), 0);
    const sentiment = urlSum % 3 === 0 ? 'positive' : urlSum % 3 === 1 ? 'negative' : 'neutral';
    const score = sentiment === 'positive' ? 0.6 + (urlSum % 30) / 100 : 
                  sentiment === 'negative' ? 0.2 + (urlSum % 30) / 100 : 0.45 + (urlSum % 10) / 100;

    // Create response object
    const response: SentimentResponse = {
      overall_sentiment: sentiment,
      sentiment_score: score,
      subjectivity: 0.4 + (urlSum % 40) / 100,
      emotions: {
        joy: sentiment === 'positive' ? 0.6 + (urlSum % 30) / 100 : 0.1 + (urlSum % 20) / 100,
        anger: sentiment === 'negative' ? 0.5 + (urlSum % 30) / 100 : 0.1 + (urlSum % 10) / 100,
        fear: sentiment === 'negative' ? 0.3 + (urlSum % 30) / 100 : 0.05 + (urlSum % 10) / 100,
        sadness: sentiment === 'negative' ? 0.4 + (urlSum % 30) / 100 : 0.05 + (urlSum % 10) / 100,
        surprise: 0.2 + (urlSum % 50) / 100,
        disgust: sentiment === 'negative' ? 0.3 + (urlSum % 20) / 100 : 0.03 + (urlSum % 7) / 100,
      },
      confidence: 0.75 + (urlSum % 20) / 100,
      url: url
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Sentiment analysis error:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
