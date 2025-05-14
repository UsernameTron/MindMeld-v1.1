import React, { useState, useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import dynamic from 'next/dynamic';
// import { tokens } from '../../../../design/tokens';

// Dynamically import Monaco editor for better performance
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false, loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded-md" /> }
);

export interface CodeEditorProps {
  /** Initial code value */
  value?: string;
  /** Language for syntax highlighting */
  language?: string;
  /** Function called when code changes */
  onChange?: (value: string | undefined) => void;
  /** Editor height */
  height?: string | number;
  /** Component size variant */
  size?: 'small' | 'medium' | 'large';
  /** Feature category for styling */
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  /** Whether editor is readonly */
  readOnly?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Optional editor options */
  options?: Record<string, any>;
}

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
}, ref) => {
  const editorRef = useRef<any>(null);
  const [mounted, setMounted] = useState(false);

  // Expose the Monaco editor instance to parent via ref
  useImperativeHandle(ref, () => editorRef.current, [mounted]);

  // Handle editor mount
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
    setMounted(true);
  };

  // Size classes
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
  };

  // Category styling
  const categoryClasses = {
    analyze: 'border-blue-500',
    chat: 'border-green-500',
    rewrite: 'border-purple-500',
    persona: 'border-yellow-500',
  };

  return (
    <div 
      className={`code-editor rounded-md overflow-hidden border ${categoryClasses[category]} ${sizeClasses[size]} ${className}`}
      data-testid="code-editor"
    >
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          folding: true,
          lineNumbers: 'on',
          readOnly,
          renderLineHighlight: 'all',
          ...options,
        }}
        className="min-h-[200px]"
      />
    </div>
  );
});

export default CodeEditor;
