import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from './atoms/Card';

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(<Card>Test Content</Card>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Card className="custom-class">Content</Card>);
    const card = screen.getByText('Content').closest('div');
    expect(card).toHaveClass('custom-class');
    expect(card).toHaveClass('bg-white');
    expect(card).toHaveClass('shadow');
  });

  it('maintains default styling while adding custom classes', () => {
    const { container } = render(<Card className="text-red-500">Content</Card>);
    const cardElement = container.firstChild;
    expect(cardElement).toHaveClass('bg-white');
    expect(cardElement).toHaveClass('rounded');
    expect(cardElement).toHaveClass('shadow');
    expect(cardElement).toHaveClass('p-4');
    expect(cardElement).toHaveClass('text-red-500');
  });
});
