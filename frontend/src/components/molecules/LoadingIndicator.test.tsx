import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator } from '../molecules/LoadingIndicator';

describe('LoadingIndicator Component', () => {
  it('renders spinner SVG element', () => {
    const { container } = render(<LoadingIndicator />);
    const svgElement = container.querySelector('svg');
    expect(svgElement).toBeInTheDocument();
    expect(svgElement).toHaveClass('animate-spin');
    expect(svgElement).toHaveClass('h-6');
    expect(svgElement).toHaveClass('w-6');
  });

  it('displays loading text', () => {
    render(<LoadingIndicator />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('centers content horizontally and vertically', () => {
    const { container } = render(<LoadingIndicator />);
    const wrapperDiv = container.firstChild;
    expect(wrapperDiv).toHaveClass('flex');
    expect(wrapperDiv).toHaveClass('items-center');
    expect(wrapperDiv).toHaveClass('justify-center');
  });
});
