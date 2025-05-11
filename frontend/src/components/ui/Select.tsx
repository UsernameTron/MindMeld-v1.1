import React from 'react';
import clsx from 'clsx';

/**
 * Option for the Select component.
 */
export interface SelectOption {
  value: string;
  label: string;
  /** Optional feature category for styling (analyze, chat, rewrite, persona) */
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  disabled?: boolean;
}

/**
 * Props for the Select component.
 * @template T extends string | number
 */
export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  /** Array of options to display */
  options: SelectOption[];
  /** Selected value */
  value: string;
  /** Change handler */
  onChange: (value: string) => void;
  /** Optional label for the select */
  label?: string;
  /** Error message for validation */
  error?: string;
  /** Feature category for styling */
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  /** Visual variant (primary, secondary, danger) */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Size of the select (sm, md, lg) */
  size?: 'sm' | 'md' | 'lg';
  /** Custom className */
  className?: string;
}

/**
 * Accessible, theme-aware Select component for MindMeld UI.
 * - Uses design tokens and Tailwind classes
 * - Supports feature category colors and Button variants
 * - ARIA compliant and keyboard accessible
 */
export const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  label,
  error,
  category,
  variant = 'primary',
  size = 'md',
  className,
  disabled,
  id,
  ...rest
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

  // Map Button variants to select styles
  const variantMap: Record<string, string> = {
    primary: 'bg-white border-blue-600 focus:ring-blue-600',
    secondary: 'bg-gray-100 border-gray-300 focus:ring-gray-400',
    danger: 'bg-white border-red-600 focus:ring-red-600',
  };
  const sizeMap: Record<string, string> = {
    sm: 'py-1 px-2 text-sm',
    md: 'py-2 px-3 text-base',
    lg: 'py-3 px-4 text-lg',
  };
  const categoryMap: Record<string, string> = {
    analyze: 'border-analyze-default focus:ring-analyze-default',
    chat: 'border-chat-default focus:ring-chat-default',
    rewrite: 'border-rewrite-default focus:ring-rewrite-default',
    persona: 'border-persona-default focus:ring-persona-default',
  };

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-sm font-medium mb-1">
          {label}
        </label>
      )}
      <select
        id={selectId}
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        aria-label={label}
        aria-invalid={!!error}
        aria-errormessage={error ? `${selectId}-error` : undefined}
        className={clsx(
          'block w-full rounded-md shadow-sm transition focus:outline-none',
          variantMap[variant],
          sizeMap[size],
          category && categoryMap[category],
          error && 'border-red-500 focus:ring-red-500',
          disabled && 'bg-gray-100 cursor-not-allowed',
          className
        )}
        role="combobox"
        {...rest}
      >
        {options.map(option => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
            aria-disabled={option.disabled}
            className={option.category ? categoryMap[option.category] : ''}
          >
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={`${selectId}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};

export default Select;
