import React from 'react';
import clsx from 'clsx';

export enum LoadingIndicatorVariant {
  SPINNER = 'spinner',
  PULSE = 'pulse',
  BAR = 'bar',
}

export interface LoadingIndicatorProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: LoadingIndicatorVariant | 'spinner' | 'pulse' | 'bar';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  ariaLabel?: string;
  className?: string;
}

const sizeClassMap = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
};

const categoryClassMap = {
  analyze: 'text-analyze',
  chat: 'text-chat',
  rewrite: 'text-rewrite',
  persona: 'text-persona',
};

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = 'md',
  variant = LoadingIndicatorVariant.SPINNER,
  category,
  ariaLabel,
  className,
}) => {
  const sizeClass = sizeClassMap[size] || sizeClassMap.md;
  const categoryClass = category ? categoryClassMap[category] : undefined;
  const label = ariaLabel || 'Loading';
  const variantStr = typeof variant === 'string' ? variant : String(variant).toLowerCase();

  let loader: React.ReactNode = null;
  if (variantStr === 'spinner') {
    loader = (
      <span
        className={clsx(
          'inline-flex items-center justify-center',
          sizeClass,
          categoryClass
        )}
        role="status"
        aria-label={label}
      >
        <span
          className={clsx(
            'animate-spin rounded-full border-2 border-current border-t-transparent',
            sizeClass
          )}
        />
        <span className="sr-only">{label}</span>
      </span>
    );
  } else if (variantStr === 'pulse') {
    loader = (
      <span
        className={clsx(
          'animate-pulse rounded-full bg-current',
          sizeClass,
          categoryClass
        )}
        role="status"
        aria-label={label}
      >
        <span className="sr-only">{label}</span>
      </span>
    );
  } else if (variantStr === 'bar') {
    loader = (
      <div
        className={clsx(
          'flex space-x-1 items-center',
          size === 'sm' ? 'h-1' : size === 'lg' ? 'h-3' : 'h-2',
          categoryClass
        )}
        role="status"
        aria-label={label}
      >
        <div className="flex-1 bg-current animate-pulse rounded h-full" />
        <div className="flex-1 bg-current animate-pulse rounded h-full delay-100" />
        <div className="flex-1 bg-current animate-pulse rounded h-full delay-200" />
        <span className="sr-only">{label}</span>
      </div>
    );
  }

  return (
    <div className={clsx('flex items-center justify-center', className)}>
      {loader}
    </div>
  );
};
