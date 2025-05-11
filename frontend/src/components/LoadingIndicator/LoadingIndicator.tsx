import React from 'react';
import clsx from 'clsx';

export interface LoadingIndicatorProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots' | 'bar' | 'skeleton';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  label?: string;
  fullPage?: boolean;
  backdrop?: boolean;
  speed?: 'slow' | 'normal' | 'fast';
  className?: string;
  labelPosition?: 'top' | 'right' | 'bottom' | 'left';
}

const sizeMap = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-16 h-16',
};

const speedMap = {
  slow: 'animate-spin-slow',
  normal: 'animate-spin',
  fast: 'animate-spin-fast',
};

const categoryMap = {
  analyze: 'text-blue-500',
  chat: 'text-green-500',
  rewrite: 'text-yellow-500',
  persona: 'text-purple-500',
};

// Custom animation speeds
const customStyles = `
@keyframes spin-slow { 100% { transform: rotate(360deg); } }
.animate-spin-slow { animation: spin-slow 2s linear infinite; }
@keyframes spin-fast { 100% { transform: rotate(360deg); } }
.animate-spin-fast { animation: spin-fast 0.5s linear infinite; }
`;

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = 'md',
  variant = 'spinner',
  category,
  label,
  fullPage,
  backdrop,
  speed = 'normal',
  className,
  labelPosition = 'bottom',
}) => {
  // ARIA
  const ariaProps = {
    role: 'status',
    'aria-live': 'polite' as 'polite',
    'aria-label': label || 'Loading',
  };

  // Loader variants
  let loader: React.ReactNode = null;
  if (variant === 'spinner') {
    loader = (
      <svg
        className={clsx('animate-spin', sizeMap[size], category && categoryMap[category], speedMap[speed])}
        style={{ display: 'inline-block' }}
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    );
  } else if (variant === 'dots') {
    loader = (
      <span className={clsx('inline-flex space-x-1', sizeMap[size])}>
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className={clsx(
              'inline-block rounded-full bg-current',
              size === 'sm' ? 'w-1.5 h-1.5' : size === 'lg' ? 'w-3 h-3' : 'w-2 h-2',
              `dot-animate dot-animate-${i}`,
              category && categoryMap[category]
            )}
          />
        ))}
      </span>
    );
  } else if (variant === 'bar') {
    loader = (
      <div className={clsx('w-full bg-gray-200 rounded', size === 'sm' ? 'h-1' : size === 'lg' ? 'h-3' : 'h-2')}>
        <div className={clsx('bar-animate', category && categoryMap[category], 'rounded h-full')} />
      </div>
    );
  } else if (variant === 'skeleton') {
    loader = (
      <div className={clsx('bg-gray-200 animate-pulse rounded', size === 'sm' ? 'h-4 w-16' : size === 'lg' ? 'h-8 w-64' : 'h-6 w-32')} />
    );
  }

  // Label positioning
  const labelNode = label ? (
    <span className={clsx('text-gray-600 dark:text-gray-300 text-sm mt-2')}>{label}</span>
  ) : null;

  const content = (
    <div className={clsx('flex items-center justify-center',
      labelPosition === 'top' && 'flex-col-reverse',
      labelPosition === 'bottom' && 'flex-col',
      labelPosition === 'left' && 'flex-row-reverse',
      labelPosition === 'right' && 'flex-row',
      className
    )} role={ariaProps.role} aria-live={ariaProps['aria-live']} aria-label={ariaProps['aria-label']}>
      {(labelPosition === 'top' || labelPosition === 'left') && labelNode}
      {loader}
      {(labelPosition === 'bottom' || labelPosition === 'right') && labelNode}
    </div>
  );

  // Full page/backdrop
  if (fullPage) {
    return (
      <>
        <style>{customStyles}
{`.dot-animate { animation: dot-bounce 1.4s infinite both; }
.dot-animate-1 { animation-delay: 0.2s; }
.dot-animate-2 { animation-delay: 0.4s; }
@keyframes dot-bounce { 0%, 80%, 100% { transform: scale(0.7); } 40% { transform: scale(1); } }
.bar-animate { animation: bar-move 1.2s linear infinite; background: currentColor; width: 30%; }
@keyframes bar-move { 0% { margin-left: 0; } 100% { margin-left: 70%; } }`}
</style>
        {backdrop && <div className="fixed inset-0 bg-black bg-opacity-40 z-40" aria-hidden="true" />}
        <div className="fixed inset-0 flex items-center justify-center z-50">
          {content}
        </div>
      </>
    );
  }

  return (
    <>
      <style>{customStyles}
{`.dot-animate { animation: dot-bounce 1.4s infinite both; }
.dot-animate-1 { animation-delay: 0.2s; }
.dot-animate-2 { animation-delay: 0.4s; }
@keyframes dot-bounce { 0%, 80%, 100% { transform: scale(0.7); } 40% { transform: scale(1); } }
.bar-animate { animation: bar-move 1.2s linear infinite; background: currentColor; width: 30%; }
@keyframes bar-move { 0% { margin-left: 0; } 100% { margin-left: 70%; } }`}
</style>
      {content}
    </>
  );
};
