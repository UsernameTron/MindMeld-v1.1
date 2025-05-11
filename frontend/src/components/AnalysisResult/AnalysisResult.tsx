import React, { useState } from 'react';
import { cn } from '../../utils/cn';
import { LoadingIndicator } from '../LoadingIndicator/LoadingIndicator';
import { ErrorDisplay } from '../ErrorDisplay/ErrorDisplay';
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
      <div className={cn('flex items-center justify-center py-8', className)} data-testid="analysis-loading">
        <LoadingIndicator variant="spinner" category={featureCategory} />
      </div>
    );
  }
  if (!feedback || feedback.length === 0) {
    return (
      <div className={cn('text-center text-slate-500 py-8', className)} data-testid="analysis-empty">
        <ErrorDisplay severity="info" title="No Results" message={emptyMessage} />
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
    <div className={cn('space-y-3', className)} data-testid="analysis-result">
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
