/**
 * MonacoMock.tsx - Testing utilities for Monaco Editor components
 * 
 * This file provides test mock implementations for Monaco Editor to make testing
 * components that use the Monaco editor easier and more reliable.
 * 
 * Usage:
 * 1. Import the mock in your test file: import { MockMonacoEditor, mockEditorRef } from '../../test-utils/monaco/MonacoMock';
 * 2. Mock next/dynamic: vi.mock('next/dynamic', () => ({ default: () => MockMonacoEditor }));
 * 3. Use the mockEditorRef in your tests to assert editor interactions
 */
import React, { useState, forwardRef, useImperativeHandle, useEffect, useRef } from 'react';
import { vi } from 'vitest';

// Keep track of editor instances across tests
export const mockEditorInstances: Record<string, any> = {};

// Editor model interface that matches Monaco's model API
interface MockEditorModel {
  id: string;
  getValue: () => string;
  setValue: (value: string) => void;
  getLanguage: () => string;
  setLanguage: (language: string) => void;
  onDidChangeContent: (callback: () => void) => { dispose: () => void };
  dispose: () => void;
}

// Create a mock editor model that mimics Monaco's model
export const createMockModel = (id: string, initialValue = '', language = 'javascript'): MockEditorModel => {
  let value = initialValue;
  let listeners: (() => void)[] = [];
  
  return {
    id,
    getValue: () => value,
    setValue: (newValue: string) => {
      value = newValue;
      listeners.forEach(listener => listener());
    },
    getLanguage: () => language,
    setLanguage: (newLanguage: string) => {
      language = newLanguage;
    },
    onDidChangeContent: (callback: () => void) => {
      listeners.push(callback);
      return {
        dispose: () => {
          listeners = listeners.filter(l => l !== callback);
        }
      };
    },
    dispose: () => {
      listeners = [];
    }
  };
};

// Monaco editor mock implementation
export const createMockEditor = (id: string) => {
  const model = createMockModel(id);
  
  return {
    id,
    model,
    getValue: () => model.getValue(),
    setValue: (value: string) => model.setValue(value),
    getModel: () => model,
    focus: vi.fn(),
    layout: vi.fn(),
    updateOptions: vi.fn(),
    getPosition: vi.fn(() => ({ lineNumber: 1, column: 1 })),
    setPosition: vi.fn(({ lineNumber, column }) => {}),
    getSelection: vi.fn(() => ({ startLineNumber: 1, startColumn: 1, endLineNumber: 1, endColumn: 1 })),
    setSelection: vi.fn(({ startLineNumber, startColumn, endLineNumber, endColumn }) => {}),
    revealLine: vi.fn((lineNumber: number) => {}),
    revealLineInCenter: vi.fn((lineNumber: number) => {}),
    revealLineInCenterIfOutsideViewport: vi.fn((lineNumber: number) => {}),
    onDidChangeModelContent: (callback: () => void) => model.onDidChangeContent(callback),
    dispose: () => {
      model.dispose();
      delete mockEditorInstances[id];
    },
    // Additional methods for testing
    _triggerChange: (newValue: string) => {
      model.setValue(newValue);
    }
  };
};

// Mock for Monaco editor component
export interface MockMonacoEditorProps {
  value?: string;
  language?: string;
  onChange?: (value: string) => void;
  onMount?: (editor: any) => void;
  height?: string | number;
  width?: string | number;
  theme?: string;
  options?: Record<string, any>;
  className?: string;
  loading?: React.ReactNode;
}

// Mock component for Monaco Editor
export const MockMonacoEditor = forwardRef<any, MockMonacoEditorProps>(({
  value = '',
  language = 'javascript',
  onChange,
  onMount,
  height = '400px',
  width = '100%',
  theme = 'vs-light',
  options = {},
  className = '',
  loading
}, ref) => {
  // Create a unique ID for this editor instance
  const id = useRef(`monaco-editor-${Date.now()}-${Math.random().toString(36).slice(2)}`).current;
  const [localValue, setLocalValue] = useState(value);
  const editorRef = useRef<any>(null);
  
  // Initialize editor if not already created
  useEffect(() => {
    if (!editorRef.current) {
      editorRef.current = createMockEditor(id);
      mockEditorInstances[id] = editorRef.current;
      
      // Call onMount callback if provided
      if (onMount) {
        onMount(editorRef.current);
      }
    }
    
    // Set initial value
    if (editorRef.current && value !== undefined) {
      editorRef.current.setValue(value);
    }
    
    // Cleanup
    return () => {
      if (editorRef.current) {
        editorRef.current.dispose();
      }
    };
  }, []);
  
  // Update value when it changes externally
  useEffect(() => {
    if (editorRef.current && value !== localValue) {
      editorRef.current.setValue(value);
      setLocalValue(value);
    }
  }, [value]);
  
  // Forward ref to the editor instance
  useImperativeHandle(ref, () => editorRef.current, [editorRef.current]);
  
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setLocalValue(newValue);
    
    if (editorRef.current) {
      editorRef.current._triggerChange(newValue);
    }
    
    if (onChange) {
      onChange(newValue);
    }
  };
  
  const containerStyle = {
    height: typeof height === 'number' ? `${height}px` : height,
    width: typeof width === 'number' ? `${width}px` : width,
    border: '1px solid #ddd',
    borderRadius: '4px',
    overflow: 'auto'
  };
  
  // Render our mock editor textarea
  return (
    <div 
      data-testid="monaco-editor"
      className={`monaco-editor-container ${className}`}
      style={containerStyle}
      data-language={language}
      data-theme={theme}
    >
      <textarea
        data-testid="mock-editor-textarea"
        value={localValue}
        onChange={handleChange}
        style={{
          width: '100%',
          height: '100%',
          resize: 'none',
          padding: '8px',
          fontFamily: 'monospace',
          fontSize: '14px',
          border: 'none',
          outline: 'none',
          backgroundColor: theme.includes('dark') ? '#1e1e1e' : '#fff',
          color: theme.includes('dark') ? '#d4d4d4' : '#000'
        }}
        readOnly={options.readOnly}
      />
    </div>
  );
});

MockMonacoEditor.displayName = 'MockMonacoEditor';

// Mock for Monaco namespace
export const MockMonaco = {
  editor: {
    create: vi.fn(createMockEditor),
    defineTheme: vi.fn(),
    setTheme: vi.fn(),
    getModels: vi.fn(() => Object.values(mockEditorInstances).map(editor => editor.getModel())),
    createModel: vi.fn(createMockModel)
  },
  languages: {
    register: vi.fn(),
    setLanguageConfiguration: vi.fn(),
    setMonarchTokensProvider: vi.fn(),
    registerCompletionItemProvider: vi.fn(() => ({ dispose: vi.fn() }))
  },
  Uri: {
    parse: vi.fn((uri: string) => ({ path: uri }))
  }
};

// Helper to mock dynamic import of Monaco
export const mockDynamicMonacoImport = () => {
  return {
    default: MockMonacoEditor,
    monaco: MockMonaco
  };
};

// Common mocks for testing
export const mockMonaco = () => {
  vi.mock('next/dynamic', () => ({
    default: () => MockMonacoEditor
  }));
  
  vi.mock('@monaco-editor/react', () => ({
    default: MockMonacoEditor,
    useMonaco: () => MockMonaco
  }));
};

// Helper to reset all mock editor instances between tests
export const resetMonacoMocks = () => {
  Object.values(mockEditorInstances).forEach(editor => {
    if (editor.dispose) editor.dispose();
  });
  
  // Reset mock function calls
  Object.values(MockMonaco.editor).forEach(fn => {
    if (typeof fn === 'function' && fn.mockReset) fn.mockReset();
  });
  
  Object.values(MockMonaco.languages).forEach(fn => {
    if (typeof fn === 'function' && fn.mockReset) fn.mockReset();
  });
};