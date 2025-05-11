import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { FeatureErrorBoundary } from './FeatureErrorBoundary.js';

interface CustomFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

describe('FeatureErrorBoundary', () => {
  it('renders fallback UI on error', () => {
    const Problem = () => { throw new Error('Oops!'); };
    render(
      <FeatureErrorBoundary>
        <Problem />
      </FeatureErrorBoundary>
    );
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it('calls onError when error is caught', () => {
    const onError = vi.fn();
    const Problem = () => { throw new Error('Oops!'); };
    render(
      <FeatureErrorBoundary onError={onError}>
        <Problem />
      </FeatureErrorBoundary>
    );
    expect(onError).toHaveBeenCalled();
  });

  it('calls onReset when retry is clicked', () => {
    const onReset = vi.fn();
    const Problem = () => { throw new Error('Oops!'); };
    render(
      <FeatureErrorBoundary onReset={onReset}>
        <Problem />
      </FeatureErrorBoundary>
    );
    fireEvent.click(screen.getByRole('button', { name: /retry/i }));
    expect(onReset).toHaveBeenCalled();
  });

  it('renders custom fallback', () => {
    const Problem = () => { throw new Error('Oops!'); };
    // Adjust CustomFallback to directly match the expected function signature
    const CustomFallback = ({ error, resetErrorBoundary }: CustomFallbackProps): React.ReactNode => (
      <div>
        <span data-testid="custom-error">Custom: {error.message}</span>
        <button onClick={resetErrorBoundary}>Reset</button>
      </div>
    );

    // Keep track of whether the Problem component should throw an error
    let shouldThrow = true;
    const ResettableProblem = () => {
      if (shouldThrow) {
        throw new Error('Oops!');
      }
      return <div>Problem Resolved</div>;
    };

    const { rerender } = render(
      <FeatureErrorBoundary fallback={CustomFallback} onReset={() => { shouldThrow = false; }}>
        <ResettableProblem />
      </FeatureErrorBoundary>
    );

    expect(screen.getByTestId('custom-error')).toBeInTheDocument();
    
    // Click the reset button
    fireEvent.click(screen.getByRole('button', { name: /reset/i }));

    // Rerender with the updated state (shouldThrow = false)
    // The FeatureErrorBoundary's onReset callback should have set shouldThrow to false.
    // The error boundary itself will re-render its children if resetKeys are not used,
    // or if the reset logic internally causes a re-render of children.
    // For this test, we need to ensure the error boundary itself resets.
    // The onReset prop in FeatureErrorBoundary is called, and then it calls this.setState({ error: null });
    // This should trigger a re-render, and ResettableProblem should no longer throw.

    // To properly test the reset, FeatureErrorBoundary needs to re-render its children.
    // The current implementation of resetErrorBoundary in the component does:
    // this.setState({ error: null }); this.props.onReset?.();
    // This will make it render `children` again.

    rerender(
      <FeatureErrorBoundary fallback={CustomFallback} onReset={() => { shouldThrow = false; }}>
        <ResettableProblem />
      </FeatureErrorBoundary>
    );

    expect(screen.queryByTestId('custom-error')).not.toBeInTheDocument();
    expect(screen.getByText('Problem Resolved')).toBeInTheDocument();
  });
});
