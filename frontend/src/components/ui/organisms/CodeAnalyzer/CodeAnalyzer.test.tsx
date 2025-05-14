import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import * as AnalyzerModule from './CodeAnalyzer';
import CodeAnalyzer from './CodeAnalyzer';
import { MockMonacoEditor, mockMonaco } from '@test-utils/monaco';
import { renderWithAuth } from '@test-utils/AuthWrapper';

// Mock the mockAnalyze function to return immediately without delay
vi.mock('./CodeAnalyzer', async () => {
  const actual = await vi.importActual<typeof AnalyzerModule>('./CodeAnalyzer');
  return {
    ...actual,
    mockAnalyze: async (code: string, language: string) => {
      if (!code.trim()) return [];
      if (code.includes('function calculateTotal')) {
        return [
          {
            id: '1',
            message: 'Missing semicolon',
            severity: 'warning',
            category: 'style',
            line: 3
          },
          {
            id: '2',
            message: 'Unused variable: tax',
            severity: 'warning',
            category: 'style',
            line: 2
          }
        ];
      }
      return [
        {
          id: '3',
          message: `No issues found in your ${language} code!`,
          severity: 'info',
          category: 'best-practice',
          line: 1
        }
      ];
    }
  };
});

// Mock the Monaco editor with a simpler approach for this specific test
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
      <div data-testid="monaco-editor" data-language={language}>
        <textarea
          data-testid="mock-editor-textarea"
          value={value || ''}
          onChange={(e) => onChange?.(e.target.value)}
        />
      </div>
    );
  }
}));

// Mock the CodeEditor component directly
vi.mock('../CodeEditor', () => ({
  default: ({ value, onChange, language }: any) => (
    <div data-testid="code-editor" className="mock-code-editor">
      <div data-testid="monaco-editor" data-language={language}>
        <textarea
          data-testid="mock-editor-textarea"
          value={value || ''}
          onChange={(e) => onChange?.(e.target.value)}
        />
      </div>
    </div>
  )
}));

// Mock the AuthContext
vi.mock('../../../../context/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

describe('CodeAnalyzer Tests', () => {
  // Set up and teardown for each test
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  // Basic rendering test
  test('renders the component with basic elements', () => {
    renderWithAuth(<CodeAnalyzer />);
    
    // Check that core UI elements are rendered
    expect(screen.getByRole('button')).toBeInTheDocument();  // Analyze button
    expect(screen.getByTestId('code-editor')).toBeInTheDocument();  // Code editor
    expect(screen.getByTestId('mock-editor-textarea')).toBeInTheDocument();  // Editor textarea
  });
  
  // Test editor interactions
  test('code editor allows input', () => {
    renderWithAuth(<CodeAnalyzer />);
    
    // Get the editor and enter some code
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const x = 5;' } });
    
    // Verify the code was entered
    expect(editor).toHaveValue('const x = 5;');
  });
  
  // Test language selector
  test('language selector changes monaco language', () => {
    renderWithAuth(<CodeAnalyzer />);
    
    // Get the language selector by its position (first select in the component)
    const languageSelector = screen.getByRole('combobox');
    
    // Change the language to Python
    fireEvent.change(languageSelector, { target: { value: 'python' } });
    
    // Verify the language changed in Monaco editor
    expect(screen.getByTestId('monaco-editor')).toHaveAttribute('data-language', 'python');
  });
});
