import React from 'react';
import { ErrorDisplay } from '../ui/molecules/ErrorDisplay/ErrorDisplay';

export interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode | ((props: { error: Error, resetErrorBoundary: () => void }) => React.ReactNode);
  onError?: (error: Error, info: React.ErrorInfo) => void;
  onReset?: () => void;
  resetKeys?: any[];
  className?: string;
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  error: Error | null;
}

/**
 * A class-based error boundary component for Pages Router compatibility
 * This component catches JavaScript errors in its child component tree,
 * logs those errors, and displays a fallback UI instead of the component
 * tree that crashed.
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };
  prevResetKeys: any[] | undefined = undefined;

  static getDerivedStateFromError(error: Error) {
    // Update state so the next render will show the fallback UI
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('ErrorBoundary caught an error:', error, info);
    }
    this.props.onError?.(error, info);
    // Optionally: send error to error tracking service here
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    if (this.state.error !== null && this.props.resetKeys && prevProps.resetKeys) {
      if (!areArraysEqual(this.props.resetKeys, prevProps.resetKeys)) {
        this.resetErrorBoundary();
      }
    }
  }

  resetErrorBoundary = () => {
    this.setState({ error: null });
    this.props.onReset?.();
  };

  render() {
    const { error } = this.state;
    const { fallback, children, className, category, showDetails } = this.props;
    
    if (error) {
      if (typeof fallback === 'function') {
        return fallback({ error, resetErrorBoundary: this.resetErrorBoundary });
      }
      
      if (fallback) {
        return fallback;
      }
      
      return (
        <div className={className} data-category={category}>
          <ErrorDisplay 
            severity="error"
            title="Something went wrong"
            message={error.message}
            code={error.name}
            onRetry={this.resetErrorBoundary}
            showStack={showDetails}
            stack={error.stack}
          />
        </div>
      );
    }
    
    return children;
  }
}

// Helper function to compare arrays
function areArraysEqual(a?: any[], b?: any[]) {
  if (a === b) return true;
  if (!a || !b) return false;
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}