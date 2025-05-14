import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SentimentVisualization, { SentimentData, SentimentScore } from './SentimentVisualization';

// Mock sentiment data for different scenarios
const positiveData: SentimentData = {
  overall: { label: 'Positive', value: 0.85 },
  scores: [
    { label: 'Positive', value: 0.85 },
    { label: 'Negative', value: 0.05 },
    { label: 'Neutral', value: 0.10 },
  ],
};
const negativeData: SentimentData = {
  overall: { label: 'Negative', value: 0.80 },
  scores: [
    { label: 'Positive', value: 0.10 },
    { label: 'Negative', value: 0.80 },
    { label: 'Neutral', value: 0.10 },
  ],
};
const neutralData: SentimentData = {
  overall: { label: 'Neutral', value: 0.60 },
  scores: [
    { label: 'Positive', value: 0.20 },
    { label: 'Negative', value: 0.20 },
    { label: 'Neutral', value: 0.60 },
  ],
};

describe('SentimentVisualization', () => {
  it('renders loading state', () => {
    render(<SentimentVisualization loading />);
    expect(screen.getByRole('status')).toBeTruthy();
    expect(screen.getByText(/loading/i)).toBeTruthy();
  });

  it('renders error state', () => {
    render(<SentimentVisualization error="Something went wrong" />);
    expect(screen.getByRole('alert')).toBeTruthy();
    expect(screen.getByText(/something went wrong/i)).toBeTruthy();
  });

  it('renders empty state', () => {
    render(<SentimentVisualization data={null} />);
    expect(screen.getByText(/no sentiment data/i)).toBeTruthy();
  });

  it('renders chart view with positive data', () => {
    render(<SentimentVisualization data={positiveData} mode="chart" />);
    expect(screen.getByLabelText(/sentiment bar chart/i)).toBeTruthy();
    expect(screen.getByText(/chart view/i)).toBeTruthy();
    expect(screen.getByText(/gauge view/i)).toBeTruthy();
    expect(screen.getByText(/color scale/i)).toBeTruthy();
  });

  it('renders gauge view with negative data', () => {
    render(<SentimentVisualization data={negativeData} mode="gauge" />);
    expect(screen.getByLabelText(/sentiment gauge/i)).toBeTruthy();
    expect(screen.getByText(/negative/i)).toBeTruthy();
  });

  it('renders color scale view with neutral data', () => {
    render(<SentimentVisualization data={neutralData} mode="color" />);
    expect(screen.getByLabelText(/sentiment color scale/i)).toBeTruthy();
    expect(screen.getByText(/neutral/i)).toBeTruthy();
  });

  it('switches visualization modes on button click', () => {
    render(<SentimentVisualization data={positiveData} mode="chart" />);
    fireEvent.click(screen.getByRole('button', { name: /gauge view/i }));
    expect(screen.getByLabelText(/sentiment gauge/i)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /color scale/i }));
    expect(screen.getByLabelText(/sentiment color scale/i)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /chart view/i }));
    expect(screen.getByLabelText(/sentiment bar chart/i)).toBeTruthy();
  });

  it('applies accessibility attributes', () => {
    render(<SentimentVisualization data={positiveData} mode="chart" />);
    expect(screen.getByLabelText(/sentiment visualization/i)).toBeTruthy();
    expect(screen.getByLabelText(/visualization mode switcher/i)).toBeTruthy();
  });

  it('handles theme switching (light/dark)', () => {
    // Simulate dark mode
    document.documentElement.classList.add('dark');
    render(<SentimentVisualization data={positiveData} mode="chart" />);
    expect(screen.getByLabelText(/sentiment bar chart/i)).toBeTruthy();
    document.documentElement.classList.remove('dark');
  });

  it('is responsive (renders at different container sizes)', () => {
    // JSDOM doesn't do real layout, but we can check that ResponsiveContainer renders
    render(<SentimentVisualization data={positiveData} mode="chart" className="max-w-xs" />);
    expect(screen.getByLabelText(/sentiment bar chart/i)).toBeTruthy();
  });

  it('handles edge case: scores missing or empty', () => {
    render(<SentimentVisualization data={{ overall: { label: 'Positive', value: 1 }, scores: [] }} mode="chart" />);
    expect(screen.getByText(/no sentiment data/i)).toBeTruthy();
  });

  it('handles edge case: overall missing', () => {
    // @ts-expect-error purposely missing overall
    render(<SentimentVisualization data={{ scores: positiveData.scores }} mode="gauge" />);
    expect(screen.getByText(/no sentiment data/i)).toBeTruthy();
  });
});
