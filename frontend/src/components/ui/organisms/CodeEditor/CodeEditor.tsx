import React, { useState, useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import dynamic from 'next/dynamic';
import { useAuth } from '../../../../context/AuthContext';

export interface CodeEditorProps {
  value?: string;
  language?: string;
  onChange?: (value: string | undefined) => void;
  height?: string | number;
  size?: 'small' | 'medium' | 'large';
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  readOnly?: boolean;
  className?: string;
  options?: Record<string, any>;
  theme?: 'light' | 'dark' | 'system';
  loadingComponent?: React.ReactNode;
}

const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  {
    ssr: false,
    loading: ({ isLoading }) =>
      isLoading ? <div className="h-64 bg-gray-100 animate-pulse rounded-md" /> : null
  }
);

const CodeEditor = forwardRef<any, CodeEditorProps>(({
  value = '',
  language = 'javascript',
  onChange,
  height = 400,
  size = 'medium',
  category = 'analyze',
  readOnly = false,
  className = '',
  options = {},
  theme = 'light',
  loadingComponent
}, ref) => {
  const { isAuthenticated } = useAuth();
  const editorRef = useRef<any>(null);

  // Theme handling
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>(
    theme === 'system'
      ? (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : (theme === 'dark' ? 'dark' : 'light')
  );

  useEffect(() => {
    if (theme === 'system' && typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        setCurrentTheme(e.matches ? 'dark' : 'light');
      };
      setCurrentTheme(mediaQuery.matches ? 'dark' : 'light');
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      setCurrentTheme(theme === 'dark' ? 'dark' : 'light');
    }
  }, [theme]);

  // Ref forwarding
  useImperativeHandle(ref, () => editorRef.current, []);
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  // Size and category styling
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
  };
  const categoryClasses = {
    analyze: 'border-blue-500',
    chat: 'border-green-500',
    rewrite: 'border-purple-500',
    persona: 'border-yellow-500',
  };

  return (
    <div
      className={`code-editor rounded-md overflow-hidden border relative ${categoryClasses[category]} ${sizeClasses[size]} ${className}`}
      data-testid="code-editor"
    >
      {!readOnly && !isAuthenticated && (
        <div className="absolute top-2 right-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded z-10">
          Read-only: Sign in to edit
        </div>
      )}
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme={currentTheme === 'dark' ? 'vs-dark' : 'light'}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          folding: true,
          lineNumbers: 'on',
          readOnly: readOnly || !isAuthenticated,
          renderLineHighlight: 'all',
          ...options,
        }}
        loading={loadingComponent}
        className="min-h-[200px]"
      />
    </div>
  );
});

CodeEditor.displayName = 'CodeEditor';

export default CodeEditor;
