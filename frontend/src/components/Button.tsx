import React from 'react';
import clsx from 'clsx';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  'aria-label'?: string;
}

/**
 * Button component supporting variants, sizes, loading state, and accessibility.
 *
 * @param {ButtonProps} props - Button props
 * @returns {JSX.Element}
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  children,
  'aria-label': ariaLabel,
  ...rest
}) => {
  const isDisabled = disabled || loading;
  const label = loading ? 'Loading…' : ariaLabel;
  return (
    <button
      type="button"
      className={clsx(
        'inline-flex items-center justify-center font-medium rounded transition focus:outline-none',
        {
          'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
          'bg-gray-100 text-gray-900 hover:bg-gray-200': variant === 'secondary',
          'bg-transparent text-blue-600 hover:bg-blue-50': variant === 'ghost',
          'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
          'opacity-50 cursor-not-allowed': isDisabled,
        }
      )}
      aria-label={label}
      aria-busy={loading ? 'true' : undefined}
      disabled={isDisabled}
      {...rest}
    >
      {loading && (
        <span className="mr-2 animate-spin h-4 w-4 border-2 border-t-transparent border-white rounded-full" aria-hidden="true" />
      )}
      <span>{children}</span>
    </button>
  );
};
