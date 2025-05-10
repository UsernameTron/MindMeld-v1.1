import React from 'react';
import clsx from 'clsx';

export type CardVariant = 'default' | 'outlined' | 'elevated';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

/**
 * MindMeld Card component - theme-aware, uses design tokens and Tailwind classes.
 */
const Card: React.FC<CardProps> = ({
  variant = 'default',
  header,
  footer,
  actions,
  children,
  className,
  ...rest
}) => {
  // Base styles from design tokens
  const base =
    'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-50 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700';
  const variants: Record<CardVariant, string> = {
    default: base,
    outlined:
      'bg-transparent dark:bg-transparent border-2 border-primary-500 dark:border-primary-400 text-primary-900 dark:text-primary-100 rounded-lg',
    elevated:
      'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-50 rounded-xl shadow-lg border border-neutral-100 dark:border-neutral-800',
  };

  return (
    <div className={clsx(variants[variant], 'transition-colors', className)} {...rest}>
      {header && (
        <div className="px-6 pt-6 pb-2 border-b border-neutral-100 dark:border-neutral-800 font-semibold text-lg flex items-center justify-between">
          <span>{header}</span>
          {actions && <div className="ml-2">{actions}</div>}
        </div>
      )}
      <div className={clsx('px-6 py-4', !header && 'pt-6')}>{children}</div>
      {footer && (
        <div className="px-6 pt-2 pb-4 border-t border-neutral-100 dark:border-neutral-800 text-sm text-neutral-600 dark:text-neutral-300">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
