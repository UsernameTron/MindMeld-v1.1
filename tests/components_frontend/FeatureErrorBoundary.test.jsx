import React from 'react';
import { render, screen } from '@testing-library/react';
import { FeatureErrorBoundary } from '../../src/components/ui/organisms/FeatureErrorBoundary/FeatureErrorBoundary';

describe('FeatureErrorBoundary', () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

    beforeEach(() => {
        consoleErrorSpy.mockClear();
    });

    afterAll(() => {
        consoleErrorSpy.mockRestore();
    });

    test('renders children when no error occurs', () => {
        render(
            <FeatureErrorBoundary featureName="TestFeature">
                <div data-testid="child-component">Child Component</div>
            </FeatureErrorBoundary>
        );

        expect(screen.getByTestId('child-component')).toBeInTheDocument();
    });

    test('renders error UI when error occurs', () => {
        // We can't directly test the error boundary with a component that throws
        // because Jest doesn't handle it well. Instead, we'll simulate the error state

        // Create a mock component that allows us to manually trigger the error state
        const ErrorTrigger = ({ shouldThrow }) => {
            if (shouldThrow) {
                throw new Error('Test error');
            }
            return <div data-testid="no-error">No Error</div>;
        };

        // Use React's act for state changes
        const { rerender } = render(
            <FeatureErrorBoundary featureName="TestFeature">
                <ErrorTrigger shouldThrow={false} />
            </FeatureErrorBoundary>
        );

        // Verify no error state initially
        expect(screen.getByTestId('no-error')).toBeInTheDocument();

        // This will cause the error boundary to catch the error
        jest.spyOn(console, 'error').mockImplementation(() => { }); // Suppress React's error logging

        // Force a render that will throw
        rerender(
            <FeatureErrorBoundary featureName="TestFeature">
                <ErrorTrigger shouldThrow={true} />
            </FeatureErrorBoundary>
        );

        // Verify error UI is shown
        expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
        expect(screen.getByText(/TestFeature/i)).toBeInTheDocument();
    });

    test('logs error details', () => {
        // Similar to the previous test, but focusing on verifying the error is logged
        const ErrorComponent = () => {
            throw new Error('Test error');
        };

        // Use special error boundary test harness
        const ErrorBoundaryTestHarness = ({
            children,
            errorBoundary
        }) => {
            const [shouldThrow, setShouldThrow] = React.useState(false);
            if (shouldThrow) {
                return React.cloneElement(errorBoundary, {}, <ErrorComponent />);
            }
            return (
                <>
                    {children}
                    <button
                        data-testid="trigger-error"
                        onClick={() => setShouldThrow(true)}
                    >
                        Trigger Error
                    </button>
                </>
            );
        };

        render(
            <ErrorBoundaryTestHarness
                errorBoundary={<FeatureErrorBoundary featureName="TestFeature" />}
            >
                <div>Child content</div>
            </ErrorBoundaryTestHarness>
        );

        // Trigger the error
        screen.getByTestId('trigger-error').click();

        // Verify error was logged
        expect(consoleErrorSpy).toHaveBeenCalled();
    });
});
