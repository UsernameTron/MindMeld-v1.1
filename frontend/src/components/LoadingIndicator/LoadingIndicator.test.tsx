import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingIndicator } from './LoadingIndicator.js';
import { vi } from 'vitest';

describe('LoadingIndicator', () => {
  it('renders without crashing', () => {
    render(<LoadingIndicator />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
