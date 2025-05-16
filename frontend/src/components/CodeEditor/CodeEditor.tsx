'use client';
import React, { Suspense, useState, useCallback, useEffect, useRef } from 'react';
import { debounce } from 'lodash';
import { cn } from '../../utils/cn';
import { LoadingIndicator } from '../ui/molecules/LoadingIndicator/LoadingIndicator';
import { FeatureErrorBoundary } from '../ui/organisms/FeatureErrorBoundary/FeatureErrorBoundary';
import { ErrorDisplay } from '../ui/molecules/ErrorDisplay/ErrorDisplay';
import type { SupportedLanguage } from '../../types/code';

const MonacoEditor = React.lazy(() => import('@monaco-editor/react').then(mod => ({ default: (mod.default as unknown as React.ComponentType<any>) })));

declare global {
  interface Window {
    monaco?: typeof import('monaco-editor');
  }
}

export interface CodeEditorProps {
  initialValue?: string;
  language?: SupportedLanguage;
  theme?: 'light' | 'dark';
  onChange?: (value: string | undefined) => void;
  readOnly?: boolean;
  height?: string;
  width?: string;
  onMount?: (editor: any) => void;
  error?: boolean;
  className?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialValue = '',
  language = 'javascript',
  theme = 'light',
  onChange,
  readOnly = false,
  height = '400px',
  width = '100%',
  onMount,
  error = false,
  className,
}) => {
  const [editorValue, setEditorValue] = useState<string>(initialValue);
  const editorRef = useRef<any>(null);

  // Debounce the onChange handler to prevent too many analysis requests
  const debouncedOnChange = useCallback(
    debounce((value) => {
      onChange?.(value);
    }, 500),
    [onChange]
  );

  const handleEditorChange = useCallback((value: string | undefined) => {
    setEditorValue(value || '');
    debouncedOnChange(value);
  }, [debouncedOnChange]);

  // Dynamic language detection and Monaco language update
  useEffect(() => {
    if (editorRef.current && window.monaco) {
      const detectLanguage = (code: string) => {
        if (code.includes('import React')) return 'typescript';
        if (code.includes('def ') && code.includes(':')) return 'python';
        return language || 'javascript';
      };
      const detectedLang = detectLanguage(editorValue);
      if (detectedLang !== language) {
        window.monaco.editor.setModelLanguage(editorRef.current.getModel(), detectedLang);
      }
    }
  }, [editorValue, language]);

  return (
    <FeatureErrorBoundary
      category="analyze"
      fallback={<ErrorDisplay severity="error" message="Failed to load code editor" title="Editor Error" />}
    >
      <div
        className={cn('code-editor-container relative', className)}
        data-testid="code-editor"
        aria-label={`Code editor for ${language}`}
        role="application"
        style={{ height, width }}
      >
        <Suspense fallback={
          <div className="w-full h-full flex items-center justify-center bg-slate-50 dark:bg-slate-900 rounded-md border border-slate-200 dark:border-slate-700">
            <LoadingIndicator variant="spinner" />
          </div>
        }>
          <MonacoEditor
            height={height}
            width={width}
            language={language}
            value={editorValue}
            theme={theme === 'dark' ? 'vs-dark' : 'light'}
            onChange={handleEditorChange}
            options={{
              readOnly,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
              fontSize: 14,
              wordWrap: 'on',
              'semanticHighlighting.enabled': true,
              'accessibilitySupport': 'on',
            }}
            onMount={(editor: any) => {
              editorRef.current = editor;
              onMount?.(editor);
            }}
          />
        </Suspense>
        {error && (
          <div className="absolute inset-0 bg-red-50 bg-opacity-50 flex items-center justify-center pointer-events-none">
            <ErrorDisplay severity="error" message="An error occurred with the code editor" title="Editor Error" />
          </div>
        )}
      </div>
    </FeatureErrorBoundary>
  );
};

export default CodeEditor;
