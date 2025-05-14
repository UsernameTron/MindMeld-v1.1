'use client';
import React from 'react';

export interface LoadingIndicatorProps {
  variant?: 'spinner' | 'dots';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ variant = 'spinner', category = 'analyze' }) => {
  return (
    <div className="flex items-center justify-center" data-testid="loading-indicator">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
    </div>
  );
};

export default LoadingIndicator;