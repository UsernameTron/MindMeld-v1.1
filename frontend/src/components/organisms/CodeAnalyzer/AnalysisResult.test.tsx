import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnalysisResult } from '@components/ui/organisms/AnalysisResult';

describe('AnalysisResult', () => {
  it('renders feedback items', () => {
    const feedback = [
      { id: 1, severity: 'error', message: 'Test error', details: 'Details' },
      { id: 2, severity: 'warning', message: 'Test warning', details: 'Details' }
    ];
    render(<AnalysisResult feedback={feedback} />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
    expect(screen.getByText('Test warning')).toBeInTheDocument();
  });
});
