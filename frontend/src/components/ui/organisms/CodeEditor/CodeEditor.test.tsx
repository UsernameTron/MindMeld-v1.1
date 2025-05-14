import React from 'react';
import { render, screen } from '@testing-library/react';
import CodeEditor from './CodeEditor';

// Mock dynamic import of Monaco editor
vi.mock('next/dynamic', () => ({
  default: () => {
    const MockMonaco = ({ value, onChange, language }: any) => (
      <div data-testid="monaco-editor" data-value={value} data-language={language}>
        <textarea
          data-testid="mock-editor-textarea"
          value={value || ''}
          onChange={e => onChange && onChange(e.target.value)}
        />
      </div>
    );
    return MockMonaco;
  }
}));

describe('CodeEditor', () => {
  test('renders the editor with default props', () => {
    render(<CodeEditor />);
    const editor = screen.getByTestId('code-editor');
    const monaco = screen.getByTestId('monaco-editor');
    expect(editor).toBeInTheDocument();
    expect(monaco).toBeInTheDocument();
    expect(monaco).toHaveAttribute('data-language', 'javascript');
  });

  test('passes the correct language to Monaco', () => {
    render(<CodeEditor language="python" />);
    const monaco = screen.getByTestId('monaco-editor');
    expect(monaco).toHaveAttribute('data-language', 'python');
  });

  test('applies category styling correctly', () => {
    render(<CodeEditor category="chat" />);
    const editor = screen.getByTestId('code-editor');
    expect(editor.className).toContain('border-green-500');
  });

  test('applies size styling correctly', () => {
    render(<CodeEditor size="large" />);
    const editor = screen.getByTestId('code-editor');
    expect(editor.className).toContain('text-lg');
  });

  test('passes initial value to editor', () => {
    const initialCode = 'const hello = "world";';
    render(<CodeEditor value={initialCode} />);
    const monaco = screen.getByTestId('monaco-editor');
    expect(monaco).toHaveAttribute('data-value', initialCode);
  });
});
