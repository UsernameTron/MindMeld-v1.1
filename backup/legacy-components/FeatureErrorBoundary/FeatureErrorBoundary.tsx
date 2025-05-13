import React from 'react';

export interface FeatureErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode | ((props: { error: Error, resetErrorBoundary: () => void }) => React.ReactNode);
  onError?: (error: Error, info: React.ErrorInfo) => void;
  onReset?: () => void;
  resetKeys?: any[];
  className?: string;
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  showDetails?: boolean;
}

interface FeatureErrorBoundaryState {
  error: Error | null;
}

export class FeatureErrorBoundary extends React.Component<FeatureErrorBoundaryProps, FeatureErrorBoundaryState> {
  state: FeatureErrorBoundaryState = { error: null };
  prevResetKeys: any[] | undefined = undefined;

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('FeatureErrorBoundary caught an error:', error, info);
    }
    this.props.onError?.(error, info);
    // Optionally: send error to error tracking service here
  }

  componentDidUpdate(prevProps: FeatureErrorBoundaryProps) {
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
      return (
        <div className={className} data-category={category}>
          {fallback || (
            <div className="p-4 bg-red-50 border border-red-400 rounded text-red-800">
              <div className="font-bold mb-2">Something went wrong.</div>
              {showDetails && (
                <pre className="text-xs bg-red-100 rounded p-2 overflow-x-auto mb-2">{error.message}\n{error.stack}</pre>
              )}
              <button
                className="mt-2 px-3 py-1 rounded bg-blue-500 text-white text-xs hover:bg-blue-600 focus:outline-none focus:ring"
                onClick={this.resetErrorBoundary}
              >
                Retry
              </button>
            </div>
          )}
        </div>
      );
    }
    return children;
  }
}

function areArraysEqual(a?: any[], b?: any[]) {
  if (a === b) return true;
  if (!a || !b) return false;
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}
