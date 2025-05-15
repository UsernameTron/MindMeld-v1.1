import React from 'react';

export interface ErrorDisplayProps {
  message: string;
  title?: string;
  severity?: 'info' | 'warning' | 'error';
  className?: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  message,
  title = 'Error',
  severity = 'error',
  className = '',
}) => {
  const color = severity === 'error' ? 'bg-red-100 text-red-700' : severity === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700';
  return (
    <div className={`p-4 rounded ${color} ${className}`} data-testid="error-display">
      <div className="font-bold mb-1">{title}</div>
      <div>{message}</div>
    </div>
  );
};

export default ErrorDisplay;
