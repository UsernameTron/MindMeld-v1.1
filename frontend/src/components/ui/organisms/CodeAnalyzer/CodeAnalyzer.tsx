import React, { useState, useRef, useCallback } from 'react';
import CodeEditor from '../CodeEditor';
import { AnalysisResult, AnalysisFeedback } from '../AnalysisResult';

// Debounce utility
function useDebounce(fn: (...args: any[]) => void, delay: number) {
  const timeout = useRef<NodeJS.Timeout | null>(null);
  return useCallback((...args: any[]) => {
    if (timeout.current) clearTimeout(timeout.current);
    timeout.current = setTimeout(() => fn(...args), delay);
  }, [fn, delay]);
}

const mockAnalyze = async (code: string, language: string): Promise<AnalysisFeedback[]> => {
  // Simulate latency
  await new Promise(res => setTimeout(res, 600));
  if (!code.trim()) return [];
  if (code.includes('error')) {
    return [
      {
        id: '1',
        message: 'Found forbidden word: error',
        severity: 'error',
        category: 'bug',
        line: 1,
        suggestion: 'Remove the word "error".'
      }
    ];
  }
  return [
    {
      id: '2',
      message: `No issues found in your ${language} code!`,
      severity: 'info',
      category: 'best-practice',
      line: 1
    }
  ];
};

const LANGUAGES = [
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
  { label: 'C++', value: 'cpp' },
];

const CodeAnalyzer: React.FC = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [results, setResults] = useState<AnalysisFeedback[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const editorRef = useRef<any>(null);

  // Debounced analyze
  const debouncedAnalyze = useDebounce(async (code: string, lang: string) => {
    setLoading(true);
    setResults(await mockAnalyze(code, lang));
    setLoading(false);
  }, 700);

  // Auto analyze on code change
  const handleCodeChange = (val: string | undefined) => {
    setCode(val ?? '');
    if (autoAnalyze) debouncedAnalyze(val ?? '', language);
  };

  // Manual analyze
  const handleAnalyze = async () => {
    setLoading(true);
    setResults(await mockAnalyze(code, language));
    setLoading(false);
  };

  // Language change
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(e.target.value);
    // Optionally re-analyze on language switch
    if (autoAnalyze) debouncedAnalyze(code, e.target.value);
  };

  // Feedback navigation
  const handleFeedbackItemClick = (feedback: AnalysisFeedback) => {
    if (feedback.line && editorRef.current) {
      // Monaco editor API: set position and reveal line
      const editor = editorRef.current;
      if (editor.setPosition && editor.revealLineInCenter) {
        editor.setPosition({ lineNumber: feedback.line, column: 1 });
        editor.revealLineInCenter(feedback.line);
        editor.focus();
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <label className="font-medium">Language:</label>
        <select
          className="border rounded px-2 py-1"
          value={language}
          onChange={handleLanguageChange}
        >
          {LANGUAGES.map(l => (
            <option key={l.value} value={l.value}>{l.label}</option>
          ))}
        </select>
        <label className="flex items-center gap-1 ml-6 cursor-pointer">
          <input
            type="checkbox"
            checked={autoAnalyze}
            onChange={e => setAutoAnalyze(e.target.checked)}
            className="accent-blue-600"
          />
          Auto Analyze
        </label>
        <button
          className="ml-auto px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
      <CodeEditor
        value={code}
        onChange={handleCodeChange}
        language={language}
        height={350}
        category="analyze"
      />
      <AnalysisResult
        feedback={results}
        loading={loading}
        featureCategory="analyze"
        onApplySuggestion={handleFeedbackItemClick}
      />
    </div>
  );
};

export default CodeAnalyzer;
