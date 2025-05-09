import React from 'react';
import { render, screen } from '@testing-library/react';
import { ErrorDisplay } from '../molecules/ErrorDisplay';

describe('ErrorDisplay Component', () => {
  it('renders error message', () => {
    render(<ErrorDisplay message="Something went wrong" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('applies error styling', () => {
    const { container } = render(<ErrorDisplay message="Error message" />);
    const errorElement = container.firstChild;
    expect(errorElement).toHaveClass('bg-red-100');
    expect(errorElement).toHaveClass('text-red-700');
    expect(errorElement).toHaveClass('rounded');
  });

  it('renders in a rounded container with padding', () => {
    const { container } = render(<ErrorDisplay message="Error with padding" />);
    const errorElement = container.firstChild;
    expect(errorElement).toHaveClass('px-4');
    expect(errorElement).toHaveClass('py-2');
  });
});
