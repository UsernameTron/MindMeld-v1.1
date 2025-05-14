import React from 'react';
import { render, screen } from '@testing-library/react';
import CodeEditor from './CodeEditor';
import { AuthProvider } from '../../../../context/AuthContext';
import { renderWithAuth } from '../../../../../test-utils/AuthWrapper';

// Mock the useAuth hook to avoid needing the full AuthProvider
vi.mock('../../../../context/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

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
  // Helper function to render with mocked auth context
  const renderWithMockAuth = (ui: React.ReactElement) => {
    return render(
      <AuthProvider>
        {ui}
      </AuthProvider>
    );
  };

  test('renders the editor with default props', () => {
    renderWithMockAuth(<CodeEditor />);
    const editor = screen.getByTestId('code-editor');
    const monaco = screen.getByTestId('monaco-editor');
    expect(editor).toBeTruthy();
    expect(monaco).toBeTruthy();
    expect(monaco).toHaveAttribute('data-language', 'javascript');
  });

  test('passes the correct language to Monaco', () => {
    renderWithMockAuth(<CodeEditor language="python" />);
    const monaco = screen.getByTestId('monaco-editor');
    expect(monaco).toHaveAttribute('data-language', 'python');
  });

  test('applies category styling correctly', () => {
    renderWithMockAuth(<CodeEditor category="chat" />);
    const editor = screen.getByTestId('code-editor');
    expect(editor.className).toContain('border-green-500');
  });

  test('applies size styling correctly', () => {
    renderWithMockAuth(<CodeEditor size="large" />);
    const editor = screen.getByTestId('code-editor');
    expect(editor.className).toContain('text-lg');
  });

  test('passes initial value to editor', () => {
    const initialCode = 'const hello = "world";';
    renderWithMockAuth(<CodeEditor value={initialCode} />);
    const monaco = screen.getByTestId('monaco-editor');
    expect(monaco).toHaveAttribute('data-value', initialCode);
  });
});
