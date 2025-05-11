import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CodeAnalyzer from './CodeAnalyzer.tsx';

vi.mock('../CodeEditor/CodeEditor.tsx', () => ({
  __esModule: true,
  CodeEditor: ({ initialValue, language, onChange }: any) => (
    <textarea
      data-testid="mock-code-editor"
      value={initialValue}
      onChange={e => onChange && onChange(e.target.value)}
      aria-label={`Code editor for ${language}`}
    />
  ),
  default: ({ initialValue, language, onChange }: any) => (
    <textarea
      data-testid="mock-code-editor"
      value={initialValue}
      onChange={e => onChange && onChange(e.target.value)}
      aria-label={`Code editor for ${language}`}
    />
  ),
}));

vi.mock('../AnalysisResult/AnalysisResult.tsx', () => ({
  __esModule: true,
  default: ({ feedback, loading, onApplySuggestion }: any) => (
    <div data-testid="mock-analysis-result">
      {loading ? 'Loading...' : feedback.map((f: any) => (
        <div key={f.id} data-testid={`mock-feedback-${f.id}`}>{f.message}</div>
      ))}
      <button data-testid="mock-apply-btn" onClick={() => onApplySuggestion && onApplySuggestion(feedback[0])}>Apply</button>
    </div>
  ),
}));

describe('CodeAnalyzer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders language and layout selects', () => {
    render(<CodeAnalyzer />);
    expect(screen.getByTestId('language-select')).toBeInTheDocument();
    expect(screen.getByTestId('layout-select')).toBeInTheDocument();
  });

  it('renders code editor and analysis result panels', () => {
    render(<CodeAnalyzer />);
    expect(screen.getByTestId('code-editor-panel')).toBeInTheDocument();
    expect(screen.getByTestId('analysis-result-panel')).toBeInTheDocument();
  });

  it('changes language and layout', () => {
    render(<CodeAnalyzer />);
    fireEvent.change(screen.getByTestId('language-select'), { target: { value: 'python' } });
    fireEvent.change(screen.getByTestId('layout-select'), { target: { value: 'stack' } });
    expect((screen.getByTestId('language-select') as HTMLSelectElement).value).toBe('python');
    expect((screen.getByTestId('layout-select') as HTMLSelectElement).value).toBe('stack');
  });

  it('triggers analysis and shows feedback', async () => {
    render(<CodeAnalyzer initialCode={'let x = 1;'} />);
    fireEvent.click(screen.getByTestId('analyze-btn'));
    await waitFor(() => expect(screen.getByTestId('mock-analysis-result')).toBeInTheDocument());
    expect(screen.getByTestId('mock-feedback-1')).toBeInTheDocument();
  });

  it('applies feedback suggestion', async () => {
    render(<CodeAnalyzer initialCode={'let x = 1;'} />);
    fireEvent.click(screen.getByTestId('analyze-btn'));
    await waitFor(() => expect(screen.getByTestId('mock-analysis-result')).toBeInTheDocument());
    fireEvent.click(screen.getByTestId('mock-apply-btn'));
    // No error thrown = pass; could extend to check code update
  });
});
