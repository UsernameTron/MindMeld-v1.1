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
    expect(card).toBeTruthy();
    expect(card?.classList.contains("rounded-lg border shadow-sm")).toBe(true);
    expect(card?.classList.contains("bg-white border-neutral-200")).toBe(true);
    expect(card?.classList.contains("p-4")).toBe(true);
    expect(card?.classList.contains("transition-all duration-200 hover:shadow-md")).toBe(true);
  });
  
  it('applies category styling correctly', () => {
    render(
      <Card data-testid="card" category="analyze">
        <CardContent>Card Content</CardContent>
      </Card>
    );
    
    const card = screen.getByTestId('card');
    expect(card?.classList.contains("border-analyze-default")).toBe(true);
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
    expect(header?.classList.contains("border-b")).toBe(true);
    expect(header?.classList.contains("pb-3")).toBe(true);
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
    expect(footer?.classList.contains("border-t")).toBe(true);
    expect(footer?.classList.contains("pt-3")).toBe(true);
    expect(footer?.classList.contains("mt-3")).toBe(true);
  });
  
  it('applies different sizes correctly', () => {
    const { rerender } = render(
      <Card data-testid="card" size="sm">
        <CardContent>Small Card</CardContent>
      </Card>
    );
    
    let card = screen.getByTestId('card');
    expect(card?.classList.contains("p-3")).toBe(true);
    
    rerender(
      <Card data-testid="card" size="lg">
        <CardContent>Large Card</CardContent>
      </Card>
    );
    
    card = screen.getByTestId('card');
    expect(card?.classList.contains("p-6")).toBe(true);
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
    expect(title?.classList.contains("font-semibold")).toBe(true);
    expect(title?.classList.contains("leading-none")).toBe(true);
    expect(title?.classList.contains("tracking-tight")).toBe(true);
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
    expect(description?.classList.contains("text-sm")).toBe(true);
    expect(description?.classList.contains("text-neutral-500")).toBe(true);
  });
});
