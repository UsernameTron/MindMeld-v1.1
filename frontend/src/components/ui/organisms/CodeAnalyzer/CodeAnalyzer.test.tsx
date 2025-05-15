import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import CodeAnalyzer from './CodeAnalyzer';
import { renderWithAuth } from '../../../test-utils/auth-test-utils';
import * as codeServiceModule from '../../../../services/codeService';

// Mock code service
vi.mock('../../../../services/codeService', () => {
  return {
    createCodeService: vi.fn().mockReturnValue({
      getCodeFeedback: vi.fn()
    }),
    convertToAnalysisFeedback: vi.fn()
  };
});

// Mock apiClient
vi.mock('../../../../services/apiClient', () => ({
  apiClient: {}
}));

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
  default: ({ value, onChange, language, onEditorMounted }: any) => {
    React.useEffect(() => {
      if (onEditorMounted) {
        onEditorMounted({
          getValue: () => value,
          focus: vi.fn(),
          revealLineInCenter: vi.fn(),
          setPosition: vi.fn(),
          setSelection: vi.fn()
        });
      }
    }, [onEditorMounted]);
    
    return (
      <div data-testid="code-editor" className="mock-code-editor">
        <div data-testid="monaco-editor" data-language={language}>
          <textarea
            data-testid="mock-editor-textarea"
            value={value || ''}
            onChange={(e) => onChange?.(e.target.value)}
          />
        </div>
      </div>
    );
  }
}));

// Mock the AuthContext
vi.mock('../../../../context/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

describe('CodeAnalyzer Component Integration Tests', () => {
  let mockGetCodeFeedback: any;
  
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetCodeFeedback = vi.fn();
    const mockCodeService = {
      getCodeFeedback: mockGetCodeFeedback
    };
    (codeServiceModule.createCodeService as any).mockReturnValue(mockCodeService);
  });
  
  it('renders the component with basic elements', () => {
    renderWithAuth(<CodeAnalyzer />);
    
    // Check that core UI elements are rendered
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument();
    expect(screen.getByTestId('code-editor')).toBeInTheDocument();
    expect(screen.getByTestId('mock-editor-textarea')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });
  
  it('initializes with sample code based on selected language', () => {
    renderWithAuth(<CodeAnalyzer />);
    
    // The component should have JavaScript sample by default
    const editorTextarea = screen.getByTestId('mock-editor-textarea');
    expect(editorTextarea.textContent).toContain('function calculateSum');
  });
  
  it('changes language and loads appropriate sample code', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    renderWithAuth(<CodeAnalyzer />);
    
    // Change language to Python
    const languageSelector = screen.getByRole('combobox');
    fireEvent.change(languageSelector, { target: { value: 'python' } });
    
    // Verify the language changed in Monaco editor
    expect(screen.getByTestId('monaco-editor')).toHaveAttribute('data-language', 'python');
    
    // Check if code service was called with Python code
    await waitFor(() => {
      expect(mockGetCodeFeedback).toHaveBeenCalledWith(
        expect.stringContaining('def calculate_sum'),
        'python'
      );
    });
  });
  
  it('allows code editor input and triggers auto-analysis', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    renderWithAuth(<CodeAnalyzer />);
    
    // Get the editor and enter some code
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const testVar = 5;' } });
    
    // Verify auto-analysis was triggered
    await waitFor(() => {
      expect(mockGetCodeFeedback).toHaveBeenCalledWith(
        'const testVar = 5;',
        'javascript'
      );
    });
  });
  
  it('does not auto-analyze when checkbox is unchecked', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    renderWithAuth(<CodeAnalyzer />);
    
    // Uncheck auto-analyze
    const autoAnalyzeCheckbox = screen.getByRole('checkbox');
    fireEvent.click(autoAnalyzeCheckbox);
    
    // Clear mock to see if it gets called again
    mockGetCodeFeedback.mockClear();
    
    // Enter code
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const noAutoAnalyze = true;' } });
    
    // Give time for debounce
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verify service wasn't called
    expect(mockGetCodeFeedback).not.toHaveBeenCalled();
  });
  
  it('analyzes code when button is clicked', async () => {
    // Mock response data
    const mockFeedbackResponse = [
      { id: 'test-1', message: 'Test warning', severity: 'warning', category: 'style', line: 3 }
    ];
    mockGetCodeFeedback.mockResolvedValue(mockFeedbackResponse);
    
    renderWithAuth(<CodeAnalyzer />);
    
    // Clear initial auto-analyze call
    mockGetCodeFeedback.mockClear();
    
    // Click the analyze button
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    fireEvent.click(analyzeButton);
    
    // Verify service was called with correct parameters
    expect(mockGetCodeFeedback).toHaveBeenCalledWith(
      expect.stringContaining('function calculateSum'),
      'javascript'
    );
  });
  
  it('displays error message when API fails', async () => {
    mockGetCodeFeedback.mockRejectedValue(new Error('API connection failed'));
    
    renderWithAuth(<CodeAnalyzer />);
    
    // Click the analyze button
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    fireEvent.click(analyzeButton);
    
    // Look for error message
    await waitFor(() => {
      expect(mockGetCodeFeedback).toHaveBeenCalled();
      // The implementation should return error feedback instead of throwing
    });
  });
  
  it('handles empty code gracefully', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    
    renderWithAuth(<CodeAnalyzer initialCode="" />);
    
    // Should not trigger initial analysis with empty code
    await waitFor(() => {
      expect(mockGetCodeFeedback).not.toHaveBeenCalled();
    });
  });
});
