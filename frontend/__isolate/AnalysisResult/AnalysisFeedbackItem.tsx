'use client';
import React, { useState } from 'react';
import { cn } from '@utils/cn';
import { Button } from '@components/atoms/Button';

// import type { AnalysisFeedback } from './AnalysisResult';
// interface AnalysisFeedbackItemProps {
//   feedback: AnalysisFeedback;
//   onApplySuggestion?: (feedback: AnalysisFeedback) => void;
// }
interface AnalysisFeedbackItemProps {
  feedback: any; // @ts-ignore TEMP for debug
  onApplySuggestion?: (feedback: any) => void;
}

const severityStyles: Record<string, string> = {
  error: 'border-red-400 bg-red-50 text-red-700',
  warning: 'border-yellow-400 bg-yellow-50 text-yellow-700',
  info: 'border-blue-400 bg-blue-50 text-blue-700',
};
const severityIcons: Record<string, React.ReactNode> = {
  error: <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01" /></svg>,
  warning: <svg className="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01M4.93 19h14.14c1.05 0 1.64-1.14 1.14-2.05l-7.07-12.2c-.5-.86-1.78-.86-2.28 0l-7.07 12.2c-.5.91.09 2.05 1.14 2.05z" /></svg>,
  info: <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 16v-4m0-4h.01" /></svg>,
};

const AnalysisFeedbackItem: React.FC<AnalysisFeedbackItemProps> = ({ feedback, onApplySuggestion }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <div
      className={cn('border rounded-md p-4 flex flex-col gap-2', severityStyles[feedback.severity])}
      data-testid={`feedback-item-${feedback.id}`}
    >
      <div className="flex items-center gap-2">
        {severityIcons[feedback.severity]}
        <span className="font-medium flex-1">
          {feedback.category && (
            <span className="uppercase text-xs font-bold mr-2 opacity-60">[{feedback.category}]</span>
          )}
          {feedback.message}
        </span>
        {feedback.suggestion && (
          <Button size="sm" variant="secondary" onClick={() => onApplySuggestion?.(feedback)} data-testid={`apply-suggestion-${feedback.id}`}>
            Apply
          </Button>
        )}
        {feedback.details && (
          <button
            className="ml-2 text-xs underline text-slate-500 hover:text-slate-700"
            onClick={() => setExpanded(e => !e)}
            data-testid={`expand-details-${feedback.id}`}
          >
            {expanded ? 'Hide details' : 'Show details'}
          </button>
        )}
      </div>
      {expanded && feedback.details && (
        <div className="mt-2 text-xs text-slate-600 bg-slate-100 rounded p-2" data-testid={`details-${feedback.id}`}>{feedback.details}</div>
      )}
    </div>
  );
};

export default AnalysisFeedbackItem;
