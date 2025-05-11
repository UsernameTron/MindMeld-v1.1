import React from 'react';
import type { FC, SVGProps } from 'react';
import { baseTokens } from '../../design/tokens/base';

/**
 * Feature category color variants for LoadingIndicator.
 */
export type LoadingIndicatorVariant = 'analyze' | 'chat' | 'rewrite' | 'persona';

export interface LoadingIndicatorProps extends React.HTMLAttributes<HTMLSpanElement> {
  /**
   * Feature category color variant.
   * @default 'analyze'
   */
  variant?: LoadingIndicatorVariant;
  /**
   * Accessible label for screen readers.
   * @default 'Loading...'
   */
  label?: string;
  /**
   * Size in pixels (width & height).
   * @default 24
   */
  size?: number;
  /**
   * Additional className for the wrapper.
   */
  className?: string;
}

const colorMap: Record<LoadingIndicatorVariant, string> = {
  analyze: baseTokens.colors.analyze.default,
  chat: baseTokens.colors.chat.default,
  rewrite: baseTokens.colors.rewrite.default,
  persona: baseTokens.colors.persona.default,
};

/**
 * Accessible, animated loading spinner for feature categories.
 */
export const LoadingIndicator: FC<LoadingIndicatorProps> = ({
  variant = 'analyze',
  label = 'Loading...',
  size = 24,
  className = '',
  ...rest
}) => (
  <span
    role="status"
    aria-live="polite"
    aria-label={label}
    className={`inline-flex items-center justify-center ${className}`}
    {...rest}
  >
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className="animate-spin motion-reduce:animate-none"
      style={{ color: colorMap[variant] }}
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
        opacity="0.2"
      />
      <path
        d="M22 12a10 10 0 0 1-10 10"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        className="origin-center"
      />
    </svg>
    <span className="sr-only">{label}</span>
  </span>
);

export default LoadingIndicator;
