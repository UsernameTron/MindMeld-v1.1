import React, { useState, useCallback, useEffect } from 'react';
import CodeEditor from '../CodeEditor/CodeEditor';
import { AnalysisResult } from '@components/ui/organisms/AnalysisResult';
import { Button } from '../Button';
import { createCodeService } from '../../services/codeService';
import { apiClient } from '../../services/apiClient';
import type { CodeAnalysisResult } from '../../services/codeService';
import { useSettingsContext } from '../../context/SettingsContext';

export interface CodeAnalyzerProps {
  initialCode?: string;
  initialLanguage?: string;
  category?: 'analyze' | 'chat' | 'rewrite' | 'persona';
  codeService?: ReturnType<typeof createCodeService>;
}

const defaultCodeService = createCodeService(apiClient);

export const CodeAnalyzer: React.FC<CodeAnalyzerProps> = ({
  initialCode,
  initialLanguage = 'javascript',
  category = 'analyze',
  codeService = defaultCodeService,
}) => {
  // Access settings context for persistence
  const { settings, updateSettings } = useSettingsContext();
  
  // Use lastCode from settings if available, otherwise use initialCode or default
  const defaultCode = settings.analyzer.lastCode || initialCode || '// Enter your code here';
  
  const [code, setCode] = useState(defaultCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [analysis, setAnalysis] = useState<CodeAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize code from settings on mount
  useEffect(() => {
    if (settings.analyzer.lastCode) {
      setCode(settings.analyzer.lastCode);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle code changes with persistence to settings
  const handleCodeChange = useCallback((value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    
    // Persist to settings context
    updateSettings({
      analyzer: {
        lastCode: newCode
      }
    });
  }, [updateSettings]);

  const handleAnalyze = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await codeService.analyzeCode(code, language);
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }, [code, language, codeService]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="flex flex-col" data-testid="code-editor-panel">
        <div className="mb-2 flex justify-between items-center">
          <select
            data-testid="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-2 py-1 rounded border text-sm"
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
          </select>
          <Button 
            data-testid="analyze-btn"
            onClick={handleAnalyze} 
            loading={loading}
          >
            Analyze Code
          </Button>
        </div>
        <CodeEditor
          initialValue={code}
          onChange={handleCodeChange}
          language={language as any}
          height="500px"
        />
      </div>
      <div data-testid="analysis-result-panel">
        <AnalysisResult 
          feedback={analysis ? analysis.issues.map((issue, idx) => ({
            id: String(idx + 1),
            message: issue.message,
            severity: issue.severity as any,
            category: 'style', // Default or map as needed
            line: issue.line,
            suggestion: issue.suggestion,
          })) : []}
          loading={loading}
          emptyMessage={error || 'No analysis results'}
        />
      </div>
    </div>
  );
};

export default CodeAnalyzer;
