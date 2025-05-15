import React, { useCallback, useRef } from 'react';
import dynamic from 'next/dynamic';
import type { Monaco } from '@monaco-editor/react';

// Dynamically import MonacoEditor with SSR disabled
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false, loading: () => <div role="status" aria-busy="true">Loading editor...</div> }
);

export type CodeEditorProps = {
  value: string;
  language: string;
  onChange: (value: string) => void;
  onLanguageChange: (lang: string) => void;
  error?: string;
  supportedLanguages?: { label: string; value: string }[];
  ariaLabel?: string;
};

const DEFAULT_LANGUAGES = [
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
  { label: 'C++', value: 'cpp' },
];

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  onChange,
  onLanguageChange,
  error,
  supportedLanguages = DEFAULT_LANGUAGES,
  ariaLabel = 'Code editor',
}) => {
  const editorRef = useRef<Monaco | null>(null);

  const handleEditorChange = useCallback((val?: string) => {
    onChange(val ?? '');
  }, [onChange]);

  return (
    <div className="code-editor-organism" aria-label={ariaLabel}>
      <label htmlFor="language-select" className="sr-only">Select language</label>
      <select
        id="language-select"
        value={language}
        onChange={e => onLanguageChange(e.target.value)}
        aria-label="Select programming language"
        className="code-editor-language-select"
      >
        {supportedLanguages.map(lang => (
          <option key={lang.value} value={lang.value}>{lang.label}</option>
        ))}
      </select>
      <div className="code-editor-container" style={{ border: error ? '1px solid #e00' : undefined }}>
        <MonacoEditor
          height="350px"
          language={language}
          value={value}
          theme="vs-dark"
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            ariaLabel,
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            tabSize: 2,
            accessibilitySupport: 'on',
          }}
        />
      </div>
      {error && (
        <div className="code-editor-error" role="alert" aria-live="assertive" tabIndex={0}>
          {error}
        </div>
      )}
    </div>
  );
};

export default CodeEditor;
