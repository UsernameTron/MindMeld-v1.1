import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import CodeAnalyzer from './CodeAnalyzer';
import { renderWithAuthAndQuery } from '../../../../../test-utils/AuthWrapper';
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

// Import the proper Monaco editor mock from test-utils
import { MockMonacoEditor } from '../../../../../test-utils/monaco/MonacoMock';

// Mock Monaco editor using the proper test utility
vi.mock('@monaco-editor/react', () => ({
  default: MockMonacoEditor,
  useMonaco: () => ({
    editor: {
      defineTheme: vi.fn(),
      setTheme: vi.fn()
    }
  })
}));

// Mock the CodeEditor component directly
vi.mock('../CodeEditor', () => ({
  default: function MockCodeEditor({ value, onChange, language, onEditorMounted, height }: any) {
    // Track editor instance for tests
    const editorRef = React.useRef<any>(null);
    
    // Create editor and call onEditorMounted immediately 
    // Use immediate effect to avoid act() warnings
    React.useEffect(() => {
      if (!editorRef.current) {
        editorRef.current = {
          getValue: () => value,
          focus: vi.fn(),
          revealLineInCenter: vi.fn(),
          setPosition: vi.fn(),
          setSelection: vi.fn(),
          layout: vi.fn()
        };
      }
      
      if (onEditorMounted) {
        onEditorMounted(editorRef.current);
      }
    }, []);
    
    // Update the mock editor when the value changes
    React.useEffect(() => {
      if (editorRef.current) {
        editorRef.current.getValue = () => value;
      }
    }, [value]);
    
    return (
      <div 
        data-testid="code-editor" 
        className="mock-code-editor"
        style={{ height: typeof height === 'number' ? `${height}px` : height }}
      >
        <MockMonacoEditor
          value={value}
          language={language}
          onChange={onChange}
          height={height}
          options={{ readOnly: false }}
        />
      </div>
    );
  }
}));

// Mock the AuthContext
vi.mock('../../../../context/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Mock the AnalysisResult component to properly display errors
vi.mock('../AnalysisResult', () => ({
  AnalysisResult: ({ feedback, loading, onApplySuggestion, emptyMessage }: any) => {
    return (
      <div data-testid="analysis-result-component">
        {loading && <div data-testid="analysis-loading">Loading analysis...</div>}
        {!loading && feedback.length === 0 && (
          <div data-testid="analysis-empty">{emptyMessage || "No results"}</div>
        )}
        {!loading && feedback.length > 0 && (
          <div>
            {feedback.map((item: any) => (
              <div 
                key={item.id} 
                data-testid={`feedback-item-${item.id}`}
                data-severity={item.severity}
                data-category={item.category}
              >
                {item.message}
                {item.suggestion && (
                  <button 
                    onClick={() => onApplySuggestion && onApplySuggestion(item)}
                    data-testid={`apply-suggestion-${item.id}`}
                  >
                    Apply Suggestion
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }
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
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
    // Check that core UI elements are rendered
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument();
    expect(screen.getByTestId('code-editor')).toBeInTheDocument();
    expect(screen.getByTestId('mock-editor-textarea')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });
  
  it('initializes with sample code based on selected language', () => {
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
    // The component should have JavaScript sample by default
    const editorTextarea = screen.getByTestId('mock-editor-textarea');
    expect(editorTextarea.textContent).toContain('function calculateSum');
  });
  
  it('changes language and loads appropriate sample code', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
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
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
    // Wait for initial render to complete
    await waitFor(() => {
      expect(screen.getByTestId('code-editor')).toBeInTheDocument();
    });
    
    // Clear initial auto-analyze call
    mockGetCodeFeedback.mockClear();
    
    // Get the editor and enter some code
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const testVar = 5;' } });
    
    // Use fake timers to control debounce timing
    vi.useFakeTimers();
    vi.advanceTimersByTime(1000);
    vi.useRealTimers();
    
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
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
    // Wait for initial render to complete
    await waitFor(() => {
      expect(screen.getByTestId('code-editor')).toBeInTheDocument();
    });
    
    // Uncheck auto-analyze
    const autoAnalyzeCheckbox = screen.getByRole('checkbox');
    fireEvent.click(autoAnalyzeCheckbox);
    
    // Clear mock to see if it gets called again
    mockGetCodeFeedback.mockClear();
    
    // Enter code
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const noAutoAnalyze = true;' } });
    
    // Use fake timers to avoid real timeouts in tests
    vi.useFakeTimers();
    
    // Fast-forward past debounce delay
    vi.advanceTimersByTime(1000);
    vi.useRealTimers();
    
    // Verify service wasn't called
    expect(mockGetCodeFeedback).not.toHaveBeenCalled();
  });
  
  it('analyzes code when button is clicked', async () => {
    // Mock response data
    const mockFeedbackResponse = [
      { id: 'test-1', message: 'Test warning', severity: 'warning', category: 'style', line: 3 }
    ];
    mockGetCodeFeedback.mockResolvedValue(mockFeedbackResponse);
    
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
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
    // Setup error response with specific test message
    const errorMessage = 'API connection failed';
    mockGetCodeFeedback.mockRejectedValue(new Error(errorMessage));
    
    renderWithAuthAndQuery(<CodeAnalyzer />);
    
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument();
    });
    
    // Clear initial calls
    mockGetCodeFeedback.mockClear();
    mockGetCodeFeedback.mockRejectedValue(new Error(errorMessage));
    
    // Click the analyze button
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    fireEvent.click(analyzeButton);
    
    // Verify the service was called
    await waitFor(() => {
      expect(mockGetCodeFeedback).toHaveBeenCalled();
    });
    
    // Wait for error state to be rendered - the implementation converts errors to feedback items
    // so we need to look for elements that would contain our error message
    await waitFor(() => {
      // The AnalysisResult component should receive the error feedback
      const errorFeedbacks = screen.getAllByText(content => 
        content.includes(errorMessage)
      );
      expect(errorFeedbacks.length).toBeGreaterThan(0);
    });
  });
  
  it('handles empty code gracefully', async () => {
    mockGetCodeFeedback.mockResolvedValue([]);
    
    renderWithAuthAndQuery(<CodeAnalyzer initialCode="" />);
    
    // Should not trigger initial analysis with empty code
    // Wait a bit to make sure no calls happen
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(mockGetCodeFeedback).not.toHaveBeenCalled();
  });
});
