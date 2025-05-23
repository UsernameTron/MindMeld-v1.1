'use client';

import React, { useRef } from 'react';
import dynamic from 'next/dynamic';
import { LoadingIndicator } from '../ui/LoadingIndicator';

// Dynamic import with SSR disabled
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react').then(mod => mod.Editor),
  { ssr: false, loading: () => <LoadingIndicator size={24} /> }
);

export type SupportedLanguage = 'javascript' | 'typescript' | 'python' | 'java' | 'go' | 'csharp';

export interface CodeEditorProps {
  initialValue?: string;
  language?: SupportedLanguage;
  onChange?: (value: string | undefined) => void;
  height?: string | number;
  className?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialValue = '',
  language = 'javascript',
  onChange,
  height = '300px',
  className,
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  return (
    <div
      className={`border rounded-md overflow-hidden ${className || ''}`}
      data-testid="code-editor"
      role="application"
    >
      <MonacoEditor
        value={initialValue}
        language={language}
        height={height}
        defaultValue={initialValue}
        onMount={handleEditorDidMount}
        onChange={onChange}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
        }}
        aria-label="Code Editor"
      />
    </div>
  );
};

export default CodeEditor;
