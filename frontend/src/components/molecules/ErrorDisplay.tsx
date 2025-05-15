import React from 'react';

export type ErrorSeverity = 'error' | 'warning' | 'info';

export interface ErrorDisplayProps {
  message: string;
  title?: string;
  severity?: ErrorSeverity;
  code?: string;
  className?: string;
  onRetry?: () => void;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const severityStyles: Record<ErrorSeverity, string> = {
  error: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900/20 dark:text-red-300',
  warning: 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/20 dark:text-yellow-300',
  info: 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/20 dark:text-blue-300',
};

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  message,
  title,
  severity = 'error',
  code,
  className,
  onRetry,
  dismissible,
  onDismiss,
}) => (
  <div
    role="alert"
    aria-live="assertive"
    className={`border rounded px-4 py-3 flex flex-col gap-1 ${severityStyles[severity]} ${className || ''}`}
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {title && <span className="font-semibold">{title}</span>}
        {code && <span className="text-xs font-mono opacity-70">[{code}]</span>}
      </div>
      {dismissible && (
        <button
          aria-label="Dismiss error"
          className="ml-2 text-lg font-bold text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          onClick={onDismiss}
        >
          ×
        </button>
      )}
    </div>
    <div className="text-sm">{message}</div>
    {onRetry && (
      <button
        className="mt-2 px-3 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-700 w-max"
        onClick={onRetry}
      >
        Retry
      </button>
    )}
  </div>
);
