import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator } from '../molecules/LoadingIndicator';

describe('LoadingIndicator Component', () => {
  it('renders spinner SVG element', () => {
    const { container } = render(<LoadingIndicator />);
    const svgElement = container.querySelector('svg');
    expect(svgElement).toBeTruthy();
    expect(svgElement?.classList.contains("animate-spin")).toBe(true);
    expect(svgElement?.classList.contains("h-6")).toBe(true);
    expect(svgElement?.classList.contains("w-6")).toBe(true);
  });

  it('displays loading text', () => {
    render(<LoadingIndicator />);
    expect(screen.getByText('Loading...')).toBeTruthy();
  });

  it('centers content horizontally and vertically', () => {
    const { container } = render(<LoadingIndicator />);
    const wrapperDiv = container.firstChild;
    expect(wrapperDiv?.classList.contains("flex")).toBe(true);
    expect(wrapperDiv?.classList.contains("items-center")).toBe(true);
    expect(wrapperDiv?.classList.contains("justify-center")).toBe(true);
  });
});
