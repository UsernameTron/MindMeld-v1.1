import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AnalysisResult from './AnalysisResult';

const mockFeedback = [
  {
    id: '1',
    message: 'Unused variable',
    severity: 'warning' as const,
    category: 'style' as const,
    line: 3,
    suggestion: 'Remove the variable',
    details: 'The variable x is declared but never used.',
  },
  {
    id: '2',
    message: 'Possible null reference',
    severity: 'error' as const,
    category: 'bug' as const,
    line: 10,
    suggestion: 'Add null check',
    details: 'The value may be null at this point.',
  },
  {
    id: '3',
    message: 'Consider using const',
    severity: 'info' as const,
    category: 'best-practice' as const,
    line: 1,
  },
];

describe('AnalysisResult', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state', () => {
    render(<AnalysisResult feedback={[]} loading />);
    expect(screen.getByTestId('analysis-loading')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(<AnalysisResult feedback={[]} />);
    expect(screen.getByTestId('analysis-empty')).toBeInTheDocument();
  });

  it('renders feedback items sorted by severity and line', () => {
    render(<AnalysisResult feedback={mockFeedback} />);
    const items = screen.getAllByTestId(/feedback-item-/);
    expect(items.length).toBe(3);
    expect(items[0]).toHaveTextContent('Possible null reference'); // error first
    expect(items[1]).toHaveTextContent('Unused variable'); // warning next
    expect(items[2]).toHaveTextContent('Consider using const'); // info last
  });

  it('expands and collapses details', () => {
    render(<AnalysisResult feedback={mockFeedback} />);
    const expandBtn = screen.getByTestId('expand-details-1');
    fireEvent.click(expandBtn);
    expect(screen.getByTestId('details-1')).toBeInTheDocument();
    fireEvent.click(expandBtn);
    expect(screen.queryByTestId('details-1')).not.toBeInTheDocument();
  });

  it('calls onApplySuggestion when Apply is clicked', () => {
    const onApply = vi.fn();
    render(<AnalysisResult feedback={mockFeedback} onApplySuggestion={onApply} />);
    const applyBtn = screen.getByTestId('apply-suggestion-1');
    fireEvent.click(applyBtn);
    expect(onApply).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }));
  });
});
