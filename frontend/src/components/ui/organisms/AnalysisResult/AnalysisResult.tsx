import React, { useState } from 'react';
import { LoadingIndicator } from '../../molecules/LoadingIndicator';
import { ErrorDisplay } from '../../molecules/ErrorDisplay';
import AnalysisFeedbackItem from './AnalysisFeedbackItem';

export type FeedbackSeverity = 'info' | 'warning' | 'error';
export type FeedbackCategory = 'style' | 'bug' | 'performance' | 'security' | 'best-practice' | 'other';
export type FeatureCategory = 'analyze' | 'chat' | 'rewrite' | 'persona';

export interface AnalysisFeedback {
  id: string;
  message: string;
  severity: FeedbackSeverity;
  category: FeedbackCategory;
  line?: number;
  suggestion?: string;
  details?: string;
}

export interface AnalysisResultProps {
  feedback: AnalysisFeedback[];
  loading?: boolean;
  emptyMessage?: string;
  featureCategory?: FeatureCategory;
  onApplySuggestion?: (feedback: AnalysisFeedback) => void;
  className?: string;
}

const severityOrder = { error: 0, warning: 1, info: 2 };

const AnalysisResult: React.FC<AnalysisResultProps> = ({
  feedback,
  loading = false,
  emptyMessage = 'No issues found.',
  featureCategory = 'analyze',
  onApplySuggestion,
  className,
}) => {
  if (loading) {
    return (
      <div className={["flex items-center justify-center py-8", className].filter(Boolean).join(' ')} data-testid="analysis-loading">
        <LoadingIndicator variant="spinner" category={featureCategory} />
      </div>
    );
  }
  const error = emptyMessage.toLowerCase().includes('error');
  if (!feedback || feedback.length === 0) {
    // Show error if emptyMessage is an error string
    const isError = emptyMessage && /failed|error/i.test(emptyMessage);
    return (
      <div className={["text-center text-slate-500 py-8", className].filter(Boolean).join(' ')} data-testid="analysis-empty">
        <ErrorDisplay severity={isError ? 'error' : 'info'} title={isError ? 'Error' : 'No Results'} message={emptyMessage} />
        {isError && (
          <div data-testid="analysis-error">{emptyMessage}</div>
        )}
      </div>
    );
  }
  const sorted = [...feedback].sort((a, b) => {
    if (severityOrder[a.severity] !== severityOrder[b.severity]) {
      return severityOrder[a.severity] - severityOrder[b.severity];
    }
    return (a.line ?? 0) - (b.line ?? 0);
  });
  return (
    <div className={["space-y-3", className].filter(Boolean).join(' ')} data-testid="analysis-result">
      <div className="font-semibold text-slate-700 dark:text-slate-200 text-base mb-2">
        {sorted.length} Feedback Item{sorted.length > 1 ? 's' : ''}
      </div>
      {sorted.map(item => (
        <AnalysisFeedbackItem
          key={item.id}
          feedback={item}
          onApplySuggestion={onApplySuggestion}
        />
      ))}
    </div>
  );
};

export default AnalysisResult;
