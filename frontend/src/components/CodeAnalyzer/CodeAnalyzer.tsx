import React from 'react';
import { cn } from '../../utils/cn.ts';
import CodeEditor from '../CodeEditor/CodeEditor.tsx';
import AnalysisResult from '../AnalysisResult/AnalysisResult.tsx';
import { Button } from '../Button.tsx';
import { FeatureErrorBoundary } from '../FeatureErrorBoundary/FeatureErrorBoundary.tsx';
import { ErrorDisplay } from '../ErrorDisplay/ErrorDisplay.tsx';
import { useCodeAnalysis } from './useCodeAnalysis.ts';

const LANGUAGES = [
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
  { label: 'Go', value: 'go' },
  { label: 'C#', value: 'csharp' },
];

const LAYOUTS = [
  { label: 'Side by Side', value: 'side' },
  { label: 'Stacked', value: 'stack' },
];

import type { SupportedLanguage } from '../CodeEditor/CodeEditor.tsx';

export interface CodeAnalyzerProps {
  initialCode?: string;
  initialLanguage?: SupportedLanguage;
  initialLayout?: 'side' | 'stack';
  className?: string;
}

const CodeAnalyzer: React.FC<CodeAnalyzerProps> = ({
  initialCode = '',
  initialLanguage = 'javascript',
  initialLayout = 'side',
  className,
}) => {
  const [layout, setLayout] = React.useState<'side' | 'stack'>(initialLayout);
  const {
    code,
    setCode,
    language,
    setLanguage,
    feedback,
    error,
    isAnalyzing,
    analyzeCode,
    applyFeedbackSuggestion,
  } = useCodeAnalysis(initialCode, initialLanguage);

  return (
    <FeatureErrorBoundary
      category="analyze"
      fallback={<ErrorDisplay severity="error" message="Failed to load analyzer" title="Analyzer Error" />}
    >
      <div className={cn('w-full max-w-5xl mx-auto p-4', className)} data-testid="code-analyzer-root">
        <div className="flex flex-col md:flex-row md:items-end gap-4 mb-4">
          <div className="flex gap-2 items-center">
            <label htmlFor="language-select" className="font-medium text-sm">Language:</label>
            <select
              id="language-select"
              data-testid="language-select"
              className="border rounded px-2 py-1 text-sm"
              value={language}
              onChange={e => setLanguage(e.target.value as any)}
            >
              {LANGUAGES.map(l => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-2 items-center">
            <label htmlFor="layout-select" className="font-medium text-sm">Layout:</label>
            <select
              id="layout-select"
              data-testid="layout-select"
              className="border rounded px-2 py-1 text-sm"
              value={layout}
              onChange={e => setLayout(e.target.value as 'side' | 'stack')}
            >
              {LAYOUTS.map(l => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>
          <Button
            onClick={analyzeCode}
            loading={isAnalyzing}
            data-testid="analyze-btn"
            className="ml-auto"
          >
            Analyze
          </Button>
        </div>
        {error && (
          <ErrorDisplay severity="error" message={error} title="Analysis Error" className="mb-4" />
        )}
        <div className={cn(
          layout === 'side' ? 'flex flex-col md:flex-row gap-6' : 'flex flex-col gap-6',
          'w-full'
        )}>
          <div className={cn('flex-1 min-w-[300px]')}
            data-testid="code-editor-panel">
            <CodeEditor
              initialValue={code}
              language={language}
              onChange={value => setCode(value || '')}
              height={layout === 'side' ? '500px' : '300px'}
              className="rounded border"
            />
          </div>
          <div className={cn('flex-1 min-w-[300px]')}
            data-testid="analysis-result-panel">
            <AnalysisResult
              feedback={feedback}
              loading={isAnalyzing}
              onApplySuggestion={applyFeedbackSuggestion}
            />
          </div>
        </div>
      </div>
    </FeatureErrorBoundary>
  );
};

export default CodeAnalyzer;
