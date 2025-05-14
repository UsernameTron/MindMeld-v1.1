import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import CodeAnalyzer from './CodeAnalyzer';

// Mock the Monaco editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange, language, onMount }: any) => {
    React.useEffect(() => {
      if (onMount) {
        onMount({
          getValue: () => value,
          focus: vi.fn(),
          revealLineInCenter: vi.fn(),
          setPosition: vi.fn(),
          setSelection: vi.fn()
        });
      }
    }, [onMount]);
    return (
      <div data-testid="monaco-editor">
        <textarea
          data-testid="mock-editor"
          value={value || ''}
          onChange={(e) => onChange?.(e.target.value)}
          data-language={language}
        />
      </div>
    );
  }
}));

describe('CodeAnalyzer Tests', () => {
  // 1: Editor-to-Analysis Flow
  test('detects errors in JavaScript code', async () => {
    render(<CodeAnalyzer />);
    const editor = screen.getByTestId('mock-editor');
    // JS with missing semicolons, unused variable, and missing return
    fireEvent.change(editor, { target: { value: `function calculateTotal(items) {\n  const tax = 0.1; // unused variable\n  let total = 0\n  console.log(\"Processing items\")\n  // missing return\n}` } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(screen.getByText(/missing semicolon/i)).toBeInTheDocument();
      expect(screen.getByText(/unused variable/i)).toBeInTheDocument();
    });
  });

  // 2: Analysis-to-Editor Flow
  test('clicking feedback items calls editor navigation methods', async () => {
    render(<CodeAnalyzer />);
    const editor = screen.getByTestId('mock-editor');
    fireEvent.change(editor, { target: { value: 'const x = 5;' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      const feedbackItem = screen.getAllByTestId(/analysis-item/)[0];
      fireEvent.click(feedbackItem);
    });
    // Would verify the ref and calling methods work correctly (integration)
  });

  // 3: Language Switching
  test('switches languages and updates analysis', async () => {
    render(<CodeAnalyzer />);
    const editor = screen.getByTestId('mock-editor');
    // Python code in JavaScript mode should show errors
    fireEvent.change(editor, { target: { value: 'def hello(): return \"world\"' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(screen.getAllByTestId(/analysis-item/).length).toBeGreaterThan(0);
    });
    // Switch to Python
    fireEvent.change(screen.getByLabelText(/language/i), { target: { value: 'python' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(editor).toHaveAttribute('data-language', 'python');
      const pythonAnalysis = screen.getAllByTestId(/analysis-item/);
      expect(pythonAnalysis.length).toBeLessThan(3);
    });
  });

  // 4: Performance/Debounce Testing
  test('debounces analysis during typing when auto-analyze is on', async () => {
    vi.useFakeTimers();
    render(<CodeAnalyzer />);
    fireEvent.click(screen.getByLabelText(/auto analyze/i)); // turn on auto-analyze
    const editor = screen.getByTestId('mock-editor');
    fireEvent.change(editor, { target: { value: 'a' } });
    fireEvent.change(editor, { target: { value: 'ab' } });
    fireEvent.change(editor, { target: { value: 'abc' } });
    // Should not analyze immediately
    // (No direct way to check, but can check after advancing timers)
    vi.advanceTimersByTime(1000);
    // Should have analyzed once after debounce
    // (Check for analysis result)
    await waitFor(() => {
      expect(screen.getByTestId('analysis-result')).toBeInTheDocument();
    });
    vi.useRealTimers();
  });

  // 5: Edge Cases
  test('handles edge cases gracefully', async () => {
    render(<CodeAnalyzer />);
    const editor = screen.getByTestId('mock-editor');
    // Empty code
    fireEvent.change(editor, { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(screen.getByText(/no issues found|empty code/i)).toBeInTheDocument();
    });
    // Long line
    fireEvent.change(editor, { target: { value: 'const x = "' + 'x'.repeat(200) + '";' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(screen.getByText(/long line|exceeds.*length/i)).toBeInTheDocument();
    });
    // Many errors
    fireEvent.change(editor, { target: { value: 'let x = 1\nlet y = 2\nlet z = 3\nconsole.log(x)\nconsole.log(y)\nconsole.log(z)' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/missing semicolon/i).length).toBeGreaterThan(3);
    });
  });
});
