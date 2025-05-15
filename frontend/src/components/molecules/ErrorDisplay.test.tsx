import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { ErrorDisplay } from '../molecules/ErrorDisplay';

describe('ErrorDisplay', () => {
  it('renders error message and default styling', () => {
    render(<ErrorDisplay message="Something went wrong" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('bg-red-100');
  });

  it('renders with severity warning', () => {
    render(<ErrorDisplay message="Warn" severity="warning" />);
    expect(screen.getByRole('alert')).toHaveClass('bg-yellow-100');
  });

  it('renders with severity info', () => {
    render(<ErrorDisplay message="Info" severity="info" />);
    expect(screen.getByRole('alert')).toHaveClass('bg-blue-100');
  });

  it('renders title and code', () => {
    render(<ErrorDisplay message="msg" title="Title" code="ERR42" />);
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('[ERR42]')).toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', () => {
    const onRetry = vi.fn();
    render(<ErrorDisplay message="msg" onRetry={onRetry} />);
    fireEvent.click(screen.getByText('Retry'));
    expect(onRetry).toHaveBeenCalled();
  });

  it('calls onDismiss when dismiss button is clicked', () => {
    const onDismiss = vi.fn();
    render(<ErrorDisplay message="msg" dismissible onDismiss={onDismiss} />);
    fireEvent.click(screen.getByLabelText('Dismiss error'));
    expect(onDismiss).toHaveBeenCalled();
  });
});
