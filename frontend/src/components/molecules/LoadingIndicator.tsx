import React from 'react';

export interface LoadingIndicatorProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  ariaLabel?: string;
}

const sizeMap = {
  sm: 20,
  md: 32,
  lg: 48,
};

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = 'md',
  color = 'var(--color-primary, #1a73e8)',
  ariaLabel = 'Loading...',
}) => {
  const spinnerSize = sizeMap[size];
  return (
    <div
      className="flex items-center justify-center"
      role="status"
      aria-live="polite"
      aria-label={ariaLabel}
    >
      <svg
        width={spinnerSize}
        height={spinnerSize}
        viewBox="0 0 44 44"
        fill="none"
        className="animate-spin"
        style={{ color }}
      >
        <circle cx="22" cy="22" r="20" stroke="#E0E0E0" strokeWidth="4" fill="none" />
        <path
          d="M22 2a20 20 0 0 1 20 20"
          stroke="#4285F4"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <path
          d="M42 22a20 20 0 0 1-20 20"
          stroke="#34A853"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <path
          d="M22 42A20 20 0 0 1 2 22"
          stroke="#FBBC05"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <path
          d="M2 22A20 20 0 0 1 22 2"
          stroke="#EA4335"
          strokeWidth="4"
          strokeLinecap="round"
        />
      </svg>
      <span className="sr-only">{ariaLabel}</span>
    </div>
  );
};
