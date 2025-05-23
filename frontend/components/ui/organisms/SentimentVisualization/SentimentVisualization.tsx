import React, { useState } from "react";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Gauge, GaugeChart, Tooltip, Legend, Bar, BarChart, XAxis, YAxis
} from "recharts";
import clsx from "clsx";

// TypeScript interfaces for emotion and sentiment data
export interface EmotionScores {
  joy: number;
  anger: number;
  fear: number;
  sadness: number;
  surprise: number;
  disgust: number;
}

export interface SentimentVisualizationProps {
  emotions?: EmotionScores | null;
  sentiment?: string;
  sentimentScore?: number;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

// Visualization modes
const MODES = ["radar", "gauge", "color"] as const;
type Mode = typeof MODES[number];

const EMOTION_LABELS: { [K in keyof EmotionScores]: string } = {
  joy: "Joy",
  anger: "Anger",
  fear: "Fear",
  sadness: "Sadness",
  surprise: "Surprise",
  disgust: "Disgust",
};

const EMOTION_COLORS: { [K in keyof EmotionScores]: string } = {
  joy: "#FFD600",
  anger: "#FF5252",
  fear: "#7C4DFF",
  sadness: "#40C4FF",
  surprise: "#FFAB00",
  disgust: "#69F0AE",
};

// Helper: transform emotion object to array for Recharts
function emotionDataArray(emotions: EmotionScores) {
  return Object.entries(emotions).map(([key, value]) => ({
    emotion: EMOTION_LABELS[key as keyof EmotionScores],
    value,
    color: EMOTION_COLORS[key as keyof EmotionScores],
    key: key as keyof EmotionScores,
  }));
}

export const SentimentVisualization: React.FC<SentimentVisualizationProps> = ({
  emotions,
  sentiment,
  sentimentScore,
  isLoading,
  error,
  className,
}) => {
  const [mode, setMode] = useState<Mode>("radar");
  const hasEmotions = !!emotions && Object.values(emotions).some((v) => v > 0);

  // Accessibility: ARIA labels
  const ariaLabel =
    mode === "radar"
      ? "Emotion radar chart"
      : mode === "gauge"
      ? "Sentiment gauge chart"
      : "Emotion color scale";

  // Error/empty/loading states
  if (isLoading) {
    return <div className={clsx("p-4 text-center", className)}>Loading analysis…</div>;
  }
  if (error) {
    return <div className={clsx("p-4 text-red-600", className)} role="alert">{error}</div>;
  }
  if (!hasEmotions && !sentiment) {
    return <div className={clsx("p-4 text-gray-500", className)}>No analysis data available.</div>;
  }

  // Visualization toggles
  const renderToggles = () => (
    <div className="flex gap-2 mb-4" role="tablist" aria-label="Visualization modes">
      {MODES.map((m) => (
        <button
          key={m}
          className={clsx(
            "px-3 py-1 rounded focus:outline-none focus-visible:ring",
            mode === m
              ? "bg-blue-600 text-white dark:bg-blue-400 dark:text-black"
              : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200"
          )}
          aria-selected={mode === m}
          aria-controls={`sentiment-viz-${m}`}
          tabIndex={mode === m ? 0 : -1}
          onClick={() => setMode(m)}
        >
          {m === "radar" ? "Radar" : m === "gauge" ? "Gauge" : "Color Scale"}
        </button>
      ))}
    </div>
  );

  // Radar chart visualization
  const renderRadar = () =>
    emotions ? (
      <ResponsiveContainer width="100%" height={320}>
        <RadarChart
          data={emotionDataArray(emotions)}
          cx="50%"
          cy="50%"
          outerRadius="80%"
        >
          <PolarGrid />
          <PolarAngleAxis dataKey="emotion" />
          <PolarRadiusAxis angle={30} domain={[0, 1]} />
          <Radar
            name="Emotions"
            dataKey="value"
            stroke="#1976d2"
            fill="#1976d2"
            fillOpacity={0.4}
          />
          <Tooltip formatter={(v: number, n: string, p: any) => `${(v * 100).toFixed(1)}%`} />
        </RadarChart>
      </ResponsiveContainer>
    ) : null;

  // Gauge visualization (sentiment only)
  const renderGauge = () => (
    <div className="flex flex-col items-center justify-center h-64">
      {typeof sentimentScore === "number" ? (
        <GaugeChart
          id="sentiment-gauge"
          nrOfLevels={20}
          colors={["#FF5252", "#FFD600", "#69F0AE"]}
          arcWidth={0.3}
          percent={sentimentScore}
          textColor="#333"
          needleColor="#1976d2"
          formatTextValue={(v: string) => `${Math.round(Number(v) * 100)}%`}
          aria-label="Sentiment gauge"
        />
      ) : (
        <div className="h-32 flex items-center justify-center text-gray-400">No sentiment score</div>
      )}
      <div className="mt-2 text-lg font-semibold" aria-live="polite">
        {sentiment ? sentiment.charAt(0).toUpperCase() + sentiment.slice(1).toLowerCase() : "Neutral"}
      </div>
    </div>
  );

  // Color scale visualization
  const renderColorScale = () =>
    emotions ? (
      <div className="flex flex-col gap-2" role="list" aria-label="Emotion color scale">
        {emotionDataArray(emotions).map(({ emotion, value, color, key }) => (
          <div key={key} className="flex items-center gap-3">
            <span
              className="inline-block w-4 h-4 rounded-full"
              style={{ background: color }}
              aria-label={emotion}
            />
            <span className="w-24" id={`emotion-label-${key}`}>{emotion}</span>
            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded h-3 relative">
              <div
                className="h-3 rounded"
                style={{
                  width: `${Math.round(value * 100)}%`,
                  background: color,
                  transition: "width 0.4s cubic-bezier(.4,2,.6,1)",
                }}
                role="progressbar"
                aria-valuenow={Math.round(value * 100)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-labelledby={`emotion-label-${key}`}
              />
            </div>
            <span className="ml-2 tabular-nums text-sm text-gray-700 dark:text-gray-200">
              {(value * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    ) : null;

  return (
    <section
      className={clsx(
        "w-full max-w-2xl mx-auto p-4 rounded shadow bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700",
        className
      )}
      aria-label="Sentiment and emotion visualization"
    >
      {renderToggles()}
      <div className="min-h-[340px]" id={`sentiment-viz-${mode}`} role="tabpanel" aria-label={ariaLabel}>
        {mode === "radar" && renderRadar()}
        {mode === "gauge" && renderGauge()}
        {mode === "color" && renderColorScale()}
      </div>
    </section>
  );
};

export default SentimentVisualization;
