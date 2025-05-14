'use client';
import React from 'react';

export interface ErrorDisplayProps {
  severity: 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ severity, title, message }) => {
  return (
    <div className="flex flex-col items-center" data-testid="error-display">
      <h3 className="font-medium text-lg">{title}</h3>
      <p className="text-sm text-slate-600">{message}</p>
    </div>
  );
};

export default ErrorDisplay;