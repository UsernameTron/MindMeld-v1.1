import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import CodeEditor from './CodeEditor';
import AnalysisResult from './AnalysisResult';
import { analyzeCode, AnalyzeCodeRequest, AnalyzeCodeResponse } from '../../../services/codeService';

const DEFAULT_CODE = `function helloWorld() {\n  console.log('Hello, world!');\n}`;
const DEFAULT_LANGUAGE = 'javascript';

export const CodeAnalyzer: React.FC = () => {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [language, setLanguage] = useState(DEFAULT_LANGUAGE);
  const [touched, setTouched] = useState(false);

  const mutation = useMutation<AnalyzeCodeResponse, any, AnalyzeCodeRequest>({
    mutationFn: analyzeCode,
  });

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!code.trim()) return;
    mutation.mutate({ code, language });
  };

  const isAnalyzeDisabled = !code.trim() || mutation.isLoading;

  return (
    <div className="code-analyzer-organism" aria-label="Code Analyzer" tabIndex={0}>
      <form onSubmit={handleAnalyze} className="code-analyzer__form">
        <CodeEditor
          value={code}
          language={language}
          onChange={setCode}
          onLanguageChange={setLanguage}
          error={touched && !code.trim() ? 'Code input cannot be empty.' : undefined}
        />
        <button
          type="submit"
          className="code-analyzer__analyze-btn"
          disabled={isAnalyzeDisabled}
          aria-disabled={isAnalyzeDisabled}
        >
          {mutation.isLoading ? 'Analyzing...' : 'Analyze Code'}
        </button>
      </form>
      <div className="code-analyzer__result">
        <AnalysisResult
          data={mutation.data || null}
          loading={mutation.isLoading}
          error={mutation.isError ? mutation.error?.message : undefined}
        />
      </div>
    </div>
  );
};

export default CodeAnalyzer;
