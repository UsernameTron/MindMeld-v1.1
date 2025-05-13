'use client';
import React, { useEffect, useRef, useState } from 'react';
import clsx from 'clsx';

export interface ErrorDisplayProps {
  title: string;
  message: string;
  severity?: 'info' | 'warning' | 'error' | 'critical';
  code?: string | number;
  dismissible?: boolean;
  onDismiss?: () => void;
  onRetry?: () => void;
  size?: 'sm' | 'md' | 'lg';
  actions?: React.ReactNode;
  showStack?: boolean;
  stack?: string;
  isToast?: boolean;
  autoHideDuration?: number;
  inline?: boolean;
  className?: string;
}

const severityIcons: Record<string, React.ReactNode> = {
  info: (
    <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 16v-4m0-4h.01" /></svg>
  ),
  warning: (
    <svg className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01M4.93 19h14.14c1.05 0 1.64-1.14 1.14-2.05l-7.07-12.2c-.5-.86-1.78-.86-2.28 0l-7.07 12.2c-.5.91.09 2.05 1.14 2.05z" /></svg>
  ),
  error: (
    <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01" /></svg>
  ),
  critical: (
    <svg className="w-6 h-6 text-red-700" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01" /></svg>
  ),
};

const severityStyles: Record<string, string> = {
  info: 'bg-blue-50 border-blue-400 text-blue-800',
  warning: 'bg-yellow-50 border-yellow-400 text-yellow-800',
  error: 'bg-red-50 border-red-400 text-red-800',
  critical: 'bg-red-100 border-red-700 text-red-900',
};

const sizeMap = {
  sm: 'p-2 text-sm',
  md: 'p-4 text-base',
  lg: 'p-6 text-lg',
};

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  title,
  message,
  severity = 'error',
  code,
  dismissible,
  onDismiss,
  onRetry,
  size = 'md',
  actions,
  showStack,
  stack,
  isToast,
  autoHideDuration,
  inline,
  className,
}) => {
  const [visible, setVisible] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-hide for toast
  useEffect(() => {
    if (isToast && autoHideDuration) {
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss?.();
      }, autoHideDuration);
      return () => clearTimeout(timer);
    }
  }, [isToast, autoHideDuration, onDismiss]);

  // Focus management for accessibility
  useEffect(() => {
    if (visible && containerRef.current && !inline && !isToast) {
      containerRef.current.focus();
    }
  }, [visible, inline, isToast]);

  if (!visible) return null;

  const icon = severityIcons[severity] || severityIcons.error;
  const style = severityStyles[severity] || severityStyles.error;

  // Animation classes
  const animation = isToast
    ? 'transition-transform duration-300 ease-in-out transform-gpu animate-toast-in'
    : 'transition-opacity duration-300 ease-in-out animate-fade-in';

  return (
    <div
      ref={containerRef}
      tabIndex={-1}
      role="alert"
      aria-live="assertive"
      className={clsx(
        'relative border rounded flex items-start gap-3 shadow-sm',
        style,
        sizeMap[size],
        isToast && 'fixed right-4 top-4 z-50 min-w-[300px] max-w-xs',
        inline ? 'inline-flex' : 'w-full',
        animation,
        className
      )}
      style={isToast ? { pointerEvents: 'auto' } : {}}
    >
      <span className="flex-shrink-0 mt-1">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold">{title}</span>
          {code && <span className="ml-2 px-2 py-0.5 rounded bg-gray-200 text-xs font-mono text-gray-700">{code}</span>}
        </div>
        <div className="mt-1 whitespace-pre-line">{message}</div>
        {showStack && stack && (
          <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-x-auto text-gray-700 max-h-40">{stack}</pre>
        )}
        {actions && <div className="mt-2 flex gap-2">{actions}</div>}
        {onRetry && (
          <button
            type="button"
            className="mt-2 px-3 py-1 rounded bg-blue-500 text-white text-xs hover:bg-blue-600 focus:outline-none focus:ring"
            onClick={onRetry}
          >
            Retry
          </button>
        )}
      </div>
      {dismissible && (
        <button
          type="button"
          aria-label="Dismiss error"
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 focus:outline-none"
          onClick={() => { setVisible(false); onDismiss?.(); }}
        >
          <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10l-4.95-4.95A1 1 0 115.05 3.636L10 8.586z" clipRule="evenodd" /></svg>
        </button>
      )}
      <style>{`
      @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
      .animate-fade-in { animation: fade-in 0.3s; }
      @keyframes toast-in { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
      .animate-toast-in { animation: toast-in 0.3s; }
      `}</style>
    </div>
  );
};
