import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card Component', () => {
  it('renders with the correct structure and content', () => {
    render(
      <Card category="analyze">
        <div>Test content</div>
      </Card>
    );
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies the correct category styling', () => {
    const { container } = render(
      <Card category="analyze">Test content</Card>
    );
    const cardElement = container.firstChild;
    const cardClasses = (cardElement as HTMLElement).className;
    expect(cardClasses).toMatch(/analyze/);
  });

  // Add more tests for variants, sizes, etc. as needed
});
