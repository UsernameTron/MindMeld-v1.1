import React from 'react';
import { render, screen } from '@testing-library/react';
import { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent 
} from './Card.js';

describe('Card', () => {
  it('renders correctly with default props', () => {
    render(
      <Card data-testid="card">
        <CardContent>Card Content</CardContent>
      </Card>
    );
    
    const card = screen.getByTestId('card');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass('rounded-lg border shadow-sm');
    expect(card).toHaveClass('bg-white border-neutral-200');
    expect(card).toHaveClass('p-4');
    expect(card).toHaveClass('transition-all duration-200 hover:shadow-md');
  });
  
  it('applies category styling correctly', () => {
    render(
      <Card data-testid="card" category="analyze">
        <CardContent>Card Content</CardContent>
      </Card>
    );
    
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('border-analyze-default');
  });
  
  it('renders card header with border when specified', () => {
    render(
      <Card data-testid="card">
        <CardHeader data-testid="header" hasBottomBorder>
          <CardTitle>Title</CardTitle>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>
    );
    
    const header = screen.getByTestId('header');
    expect(header).toHaveClass('border-b');
    expect(header).toHaveClass('pb-3');
  });
  
  it('renders card footer with border when specified', () => {
    render(
      <Card data-testid="card">
        <CardContent>Content</CardContent>
        <CardFooter data-testid="footer" hasTopBorder>
          Footer
        </CardFooter>
      </Card>
    );
    
    const footer = screen.getByTestId('footer');
    expect(footer).toHaveClass('border-t');
    expect(footer).toHaveClass('pt-3');
    expect(footer).toHaveClass('mt-3');
  });
  
  it('applies different sizes correctly', () => {
    const { rerender } = render(
      <Card data-testid="card" size="sm">
        <CardContent>Small Card</CardContent>
      </Card>
    );
    
    let card = screen.getByTestId('card');
    expect(card).toHaveClass('p-3');
    
    rerender(
      <Card data-testid="card" size="lg">
        <CardContent>Large Card</CardContent>
      </Card>
    );
    
    card = screen.getByTestId('card');
    expect(card).toHaveClass('p-6');
  });
  
  it('renders card title with correct styling', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle data-testid="title">Card Title</CardTitle>
        </CardHeader>
      </Card>
    );
    
    const title = screen.getByTestId('title');
    expect(title).toHaveClass('font-semibold');
    expect(title).toHaveClass('leading-none');
    expect(title).toHaveClass('tracking-tight');
    expect(title.tagName).toBe('H3');
  });
  
  it('renders card description with correct styling', () => {
    render(
      <Card>
        <CardHeader>
          <CardDescription data-testid="description">Card Description</CardDescription>
        </CardHeader>
      </Card>
    );
    
    const description = screen.getByTestId('description');
    expect(description).toHaveClass('text-sm');
    expect(description).toHaveClass('text-neutral-500');
  });
});
