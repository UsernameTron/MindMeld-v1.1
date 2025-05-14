import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

// --- TypeScript interfaces ---
export interface SentimentScore {
  label: string; // e.g. 'Positive', 'Negative', 'Neutral'
  value: number; // 0-1
}

export interface SentimentData {
  overall: SentimentScore; // e.g. { label: 'Positive', value: 0.82 }
  scores: SentimentScore[]; // e.g. [ { label: 'Positive', value: 0.82 }, ... ]
}

export interface SentimentVisualizationProps {
  data?: SentimentData | null;
  loading?: boolean;
  error?: string | null;
  mode?: 'chart' | 'gauge' | 'color';
  onModeChange?: (mode: 'chart' | 'gauge' | 'color') => void;
  className?: string;
}

// --- Color palettes for light/dark mode ---
const SENTIMENT_COLORS = {
  Positive: {
    light: '#22c55e', // green-500
    dark: '#4ade80',
  },
  Negative: {
    light: '#ef4444', // red-500
    dark: '#f87171',
  },
  Neutral: {
    light: '#fbbf24', // yellow-400
    dark: '#fde68a',
  },
};

function getColor(label: string, theme: 'light' | 'dark') {
  return SENTIMENT_COLORS[label as keyof typeof SENTIMENT_COLORS]?.[theme] || '#64748b';
}

const SentimentVisualization: React.FC<SentimentVisualizationProps> = ({
  data,
  loading = false,
  error = null,
  mode: initialMode = 'chart',
  onModeChange,
  className,
}) => {
  const [mode, setMode] = useState<'chart' | 'gauge' | 'color'>(initialMode);
  // Theme detection (tailwind or custom)
  const theme = typeof window !== 'undefined' && document.documentElement.classList.contains('dark') ? 'dark' : 'light';

  // --- Accessibility: ARIA labels, roles, etc. ---
  const handleModeChange = (newMode: 'chart' | 'gauge' | 'color') => {
    setMode(newMode);
    onModeChange?.(newMode);
  };

  // --- Loading/Error/Empty States ---
  if (loading) {
    return <div className={`flex items-center justify-center py-8 ${className || ''}`} role="status" aria-busy="true">Loading sentiment analysis...</div>;
  }
  if (error) {
    return <div className={`text-center text-red-500 py-8 ${className || ''}`} role="alert" aria-live="assertive">{error}</div>;
  }
  if (!data || (Array.isArray(data.scores) && data.scores.length === 0) || (mode === 'gauge' && (!data.overall || typeof data.overall.value !== 'number'))) {
    return <div className={`text-center text-slate-500 py-8 ${className || ''}`}>No sentiment data</div>;
  }

  // --- Visualization Mode Switcher ---
  const modes = [
    { key: 'chart', label: 'Chart View' },
    { key: 'gauge', label: 'Gauge View' },
    { key: 'color', label: 'Color Scale' },
  ];

  // --- Chart View ---
  const renderChart = () => (
    <div aria-label="Sentiment Bar Chart" role="region" style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data.scores}>
          <XAxis dataKey="label" stroke={theme === 'dark' ? '#e5e7eb' : '#334155'} />
          <YAxis domain={[0, 1]} stroke={theme === 'dark' ? '#e5e7eb' : '#334155'} />
          <Tooltip />
          <Bar dataKey="value">
            {data.scores.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={getColor(entry.label, theme)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  // --- Gauge View ---
  const renderGauge = () => {
    if (!data.overall || typeof data.overall.value !== 'number') {
      return <div className="text-center text-slate-500 py-8">No sentiment data</div>;
    }
    // Pie chart as a gauge (single value)
    const gaugeValue = data.overall.value;
    const gaugeColor = getColor(data.overall.label, theme);
    return (
      <div className="flex flex-col items-center" aria-label="Sentiment Gauge">
        <ResponsiveContainer width={180} height={120}>
          <PieChart>
            <Pie
              data={[{ value: gaugeValue }, { value: 1 - gaugeValue }]}
              startAngle={180}
              endAngle={0}
              innerRadius={50}
              outerRadius={60}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={gaugeColor} />
              <Cell fill={theme === 'dark' ? '#334155' : '#e5e7eb'} />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <span className="mt-2 text-lg font-semibold" style={{ color: gaugeColor }}>{data.overall.label} ({Math.round(gaugeValue * 100)}%)</span>
      </div>
    );
  };

  // --- Color Scale View ---
  const renderColorScale = () => {
    // Map sentiment to a color bar
    return (
      <div className="flex flex-col items-center" aria-label="Sentiment Color Scale">
        <div className="flex w-full max-w-xs h-8 rounded overflow-hidden border border-slate-200 dark:border-slate-700">
          {data.scores.map((score, idx) => (
            <div
              key={score.label}
              style={{
                width: `${score.value * 100}%`,
                background: getColor(score.label, theme),
                transition: 'width 0.5s',
              }}
              className="h-full"
              aria-label={`${score.label}: ${Math.round(score.value * 100)}%`}
            />
          ))}
        </div>
        <div className="flex justify-between w-full max-w-xs mt-2 text-xs text-slate-600 dark:text-slate-300">
          {data.scores.map(score => (
            <span key={score.label}>{score.label}</span>
          ))}
        </div>
      </div>
    );
  };

  // --- Main Render ---
  return (
    <section
      className={`w-full max-w-xl mx-auto p-4 rounded-lg shadow bg-white dark:bg-slate-800 ${className || ''}`}
      aria-label="Sentiment Visualization"
    >
      <nav className="flex justify-end gap-2 mb-4" aria-label="Visualization Mode Switcher">
        {modes.map(m => (
          <button
            key={m.key}
            type="button"
            className={`px-3 py-1 rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 text-sm font-medium transition-colors ${mode === m.key ? 'bg-blue-500 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200'}`}
            aria-pressed={mode === m.key}
            aria-label={m.label}
            onClick={() => handleModeChange(m.key as 'chart' | 'gauge' | 'color')}
          >
            {m.label}
          </button>
        ))}
      </nav>
      <div className="min-h-[220px] flex items-center justify-center">
        {mode === 'chart' && renderChart()}
        {mode === 'gauge' && renderGauge()}
        {mode === 'color' && renderColorScale()}
      </div>
    </section>
  );
};

export default SentimentVisualization;
