import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator, LoadingIndicatorVariant } from '../../../../src/components/ui/LoadingIndicator';

describe('LoadingIndicator', () => {
  it('renders with default props', () => {
    render(<LoadingIndicator />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByLabelText('Loading...')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toHaveClass('sr-only');
  });

  it('supports all feature category variants', () => {
    const variants: LoadingIndicatorVariant[] = ['analyze', 'chat', 'rewrite', 'persona'];
    variants.forEach(variant => {
      render(<LoadingIndicator variant={variant} label={variant} />);
      expect(screen.getByLabelText(variant)).toBeInTheDocument();
    });
  });

  it('applies custom size', () => {
    render(<LoadingIndicator size={40} />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveAttribute('width', '40');
    expect(svg).toHaveAttribute('height', '40');
  });

  it('applies additional className', () => {
    render(<LoadingIndicator className="test-class" />);
    expect(screen.getByRole('status')).toHaveClass('test-class');
  });

  it('is accessible with proper ARIA attributes', () => {
    render(<LoadingIndicator label="Loading data" />);
    const el = screen.getByRole('status');
    expect(el).toHaveAttribute('aria-live', 'polite');
    expect(el).toHaveAttribute('aria-label', 'Loading data');
  });
});
