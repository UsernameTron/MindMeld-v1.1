import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from './atoms/Card';

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(<Card>Test Content</Card>);
    expect(screen.getByText('Test Content')).toBeTruthy();
  });

  it('applies custom className', () => {
    render(<Card className="custom-class">Content</Card>);
    const card = screen.getByText('Content').closest('div');
    expect(card?.classList.contains("custom-class")).toBe(true);
    expect(card?.classList.contains("bg-white")).toBe(true);
    expect(card?.classList.contains("shadow")).toBe(true);
  });

  it('maintains default styling while adding custom classes', () => {
    const { container } = render(<Card className="text-red-500">Content</Card>);
    const cardElement = container.firstChild;
    expect(cardElement?.classList.contains("bg-white")).toBe(true);
    expect(cardElement?.classList.contains("rounded")).toBe(true);
    expect(cardElement?.classList.contains("shadow")).toBe(true);
    expect(cardElement?.classList.contains("p-4")).toBe(true);
    expect(cardElement?.classList.contains("text-red-500")).toBe(true);
  });
});
