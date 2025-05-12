import React from 'react';
import { render, screen } from '@testing-library/react';
import { ErrorDisplay } from '../molecules/ErrorDisplay';

describe('ErrorDisplay Component', () => {
  it('renders error message', () => {
    render(<ErrorDisplay message="Something went wrong" />);
    const element = screen.getByText('Something went wrong');
    expect(element).toBeTruthy();
  });

  it('applies error styling', () => {
    const { container } = render(<ErrorDisplay message="Error message" />);
    const errorElement = container.firstChild as HTMLElement;
    expect(errorElement.classList.contains('bg-red-100')).toBe(true);
    expect(errorElement.classList.contains('text-red-700')).toBe(true);
    expect(errorElement.classList.contains('rounded')).toBe(true);
  });

  it('renders in a rounded container with padding', () => {
    const { container } = render(<ErrorDisplay message="Error with padding" />);
    const errorElement = container.firstChild as HTMLElement;
    expect(errorElement.classList.contains('px-4')).toBe(true);
    expect(errorElement.classList.contains('py-2')).toBe(true);
  });
});
