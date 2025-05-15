import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator } from '../molecules/LoadingIndicator';

describe('LoadingIndicator', () => {
  it('renders with default (md) size', () => {
    render(<LoadingIndicator />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveAttribute('width', '32');
    expect(svg).toHaveAttribute('height', '32');
  });

  it('renders with sm size', () => {
    render(<LoadingIndicator size="sm" />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveAttribute('width', '20');
    expect(svg).toHaveAttribute('height', '20');
  });

  it('renders with lg size', () => {
    render(<LoadingIndicator size="lg" />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveAttribute('width', '48');
    expect(svg).toHaveAttribute('height', '48');
  });

  it('applies custom color', () => {
    render(<LoadingIndicator color="#123456" />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveStyle({ color: '#123456' });
  });

  it('sets aria-label for accessibility', () => {
    render(<LoadingIndicator ariaLabel="Please wait" />);
    expect(screen.getByLabelText('Please wait')).toBeInTheDocument();
  });
});
