import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator, LoadingIndicatorVariant } from './LoadingIndicator.tsx';

describe('LoadingIndicator', () => {
  it('renders without crashing', () => {
    render(<LoadingIndicator />);
    // Should have a status role for accessibility
    const loadingElement = screen.getByRole('status');
    expect(loadingElement).toBeInTheDocument();
  });

  it('includes a screen reader only text by default', () => {
    render(<LoadingIndicator />);
    const srText = screen.getByText('Loading');
    expect(srText).toBeInTheDocument();
    // Should be visually hidden
    expect(srText).toHaveClass('sr-only');
  });

  it('uses custom ariaLabel when provided', () => {
    render(<LoadingIndicator ariaLabel="Processing your request" />);
    const loadingElement = screen.getByLabelText('Processing your request');
    expect(loadingElement).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<LoadingIndicator size="sm" />);
    let loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('w-4');

    rerender(<LoadingIndicator size="md" />);
    loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('w-6');

    rerender(<LoadingIndicator size="lg" />);
    loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('w-8');
  });

  it('applies feature category colors correctly', () => {
    const { rerender } = render(<LoadingIndicator category="analyze" />);
    let loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('text-analyze');

    rerender(<LoadingIndicator category="chat" />);
    loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('text-chat');
  });

  it('renders spinner variant by default', () => {
    render(<LoadingIndicator />);
    const loadingElement = screen.getByRole('status');
    // Spinner uses animate-spin and border-t-transparent
    expect(loadingElement.querySelector('.animate-spin')).toBeInTheDocument();
    expect(loadingElement.querySelector('.border-t-transparent')).toBeInTheDocument();
  });

  it('renders pulse variant correctly', () => {
    render(<LoadingIndicator variant={LoadingIndicatorVariant.PULSE} />);
    const loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('animate-pulse');
  });

  it('renders bar variant correctly', () => {
    render(<LoadingIndicator variant={LoadingIndicatorVariant.BAR} />);
    const loadingElement = screen.getByRole('status');
    expect(loadingElement).toHaveClass('flex');
    // Should have multiple child elements for the bars
    const childElements = loadingElement.querySelectorAll('div');
    expect(childElements.length).toBeGreaterThan(1);
  });

  it('accepts and applies additional className', () => {
    render(<LoadingIndicator className="custom-class" />);
    const wrapper = screen.getByRole('status').parentElement;
    expect(wrapper).toHaveClass('custom-class');
  });

  // TODO: Add tests for new variants, fullPage/backdrop, labelPosition, speed, etc. when implemented
});

// TODO: For future enhancements, add tests for:
// - Additional variants (e.g., dots, skeleton)
// - Full page/backdrop rendering
// - Custom label positions
// - Animation speed prop
// - More advanced accessibility scenarios
// - Visual regression testing
