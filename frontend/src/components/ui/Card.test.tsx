import React from 'react';
import { render, screen } from '@testing-library/react';
import Card from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Content</Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders header and footer', () => {
    render(<Card header="Header" footer="Footer">Content</Card>);
    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('renders actions in header', () => {
    render(
      <Card header="Header" actions={<button>Action</button>}>
        Content
      </Card>
    );
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  it('applies variant classes', () => {
    const { container } = render(<Card variant="outlined">Content</Card>);
    expect((container.firstChild as HTMLElement)?.classList.contains("border-2")).toBe(true);
  });

  it('renders without header/footer', () => {
    render(<Card>Content</Card>);
    expect(screen.queryByText('Header')).not.toBeInTheDocument();
    expect(screen.queryByText('Footer')).not.toBeInTheDocument();
  });
});
