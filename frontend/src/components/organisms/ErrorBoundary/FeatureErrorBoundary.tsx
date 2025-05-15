import React, { Component, ErrorInfo, ReactNode } from 'react';

interface FeatureErrorBoundaryProps {
  name?: string;
  children: ReactNode;
  fallback?: (args: { error: Error; resetErrorBoundary: () => void }) => ReactNode;
}

interface FeatureErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class FeatureErrorBoundary extends Component<FeatureErrorBoundaryProps, FeatureErrorBoundaryState> {
  state: FeatureErrorBoundaryState = {
    hasError: false,
    error: null,
  };

  static getDerivedStateFromError(error: Error): FeatureErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to monitoring service if needed
    // eslint-disable-next-line no-console
    console.error(`Error in ${this.props.name}:`, error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback && this.state.error) {
        return this.props.fallback({ error: this.state.error, resetErrorBoundary: this.handleReset });
      }
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="p-4 border border-red-300 rounded-md bg-red-50 dark:bg-red-900/20"
        >
          <h3 className="text-lg font-medium text-red-800 dark:text-red-300">Component Error</h3>
          <p className="mt-2 text-sm text-red-700 dark:text-red-300">
            The {this.props.name || 'feature'} component encountered an error.
          </p>
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">
            {this.state.error?.message}
          </p>
          <button
            className="mt-3 px-3 py-1 text-sm bg-red-700 text-white rounded-md hover:bg-red-800"
            onClick={this.handleReset}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
