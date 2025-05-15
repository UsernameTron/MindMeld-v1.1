import React, { useState, useRef, useCallback, useEffect } from 'react';
import CodeEditor from '../CodeEditor';
import { AnalysisResult, AnalysisFeedback } from '../AnalysisResult';
import { createCodeService } from '../../../../services/codeService';
import { apiClient } from '../../../../services/apiClient';

// Debounce utility
function useDebounce(fn: (...args: any[]) => void, delay: number) {
  const timeout = useRef<NodeJS.Timeout | null>(null);
  return useCallback((...args: any[]) => {
    if (timeout.current) clearTimeout(timeout.current);
    timeout.current = setTimeout(() => fn(...args), delay);
  }, [fn, delay]);
}

const LANGUAGES = [
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
  { label: 'C++', value: 'cpp' },
];

// Sample snippets for each language
const SAMPLE_SNIPPETS: Record<string, string> = {
  javascript: `function calculateSum(numbers) {
  return numbers.reduce((sum, num) => sum + num, 0);
}

// Example usage
const result = calculateSum([1, 2, 3, 4, 5]);
console.log(result);`,
  
  typescript: `function calculateSum(numbers: number[]): number {
  return numbers.reduce((sum, num) => sum + num, 0);
}

// Example usage
const result: number = calculateSum([1, 2, 3, 4, 5]);
console.log(result);`,
  
  python: `def calculate_sum(numbers):
    return sum(numbers)

# Example usage
result = calculate_sum([1, 2, 3, 4, 5])
print(result)`,
  
  java: `public class SumCalculator {
    public static int calculateSum(int[] numbers) {
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        return sum;
    }
    
    public static void main(String[] args) {
        int[] numbers = {1, 2, 3, 4, 5};
        int result = calculateSum(numbers);
        System.out.println(result);
    }
}`,
  
  cpp: `#include <iostream>
#include <vector>
#include <numeric>

int calculateSum(const std::vector<int>& numbers) {
    return std::accumulate(numbers.begin(), numbers.end(), 0);
}

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    int result = calculateSum(numbers);
    std::cout << result << std::endl;
    return 0;
}`
};

interface CodeAnalyzerProps {
  initialCode?: string;
  initialLanguage?: string;
}

const CodeAnalyzer: React.FC<CodeAnalyzerProps> = ({
  initialCode,
  initialLanguage = 'javascript'
}) => {
  // Initialize state with provided props or defaults
  const [code, setCode] = useState(initialCode || SAMPLE_SNIPPETS[initialLanguage] || '');
  const [language, setLanguage] = useState(initialLanguage);
  const [results, setResults] = useState<AnalysisFeedback[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [codeService] = useState(() => createCodeService(apiClient));
  const editorRef = useRef<any>(null);

  // Analyze the code using the service
  const analyzeCode = async (codeToAnalyze: string, lang: string) => {
    if (!codeToAnalyze.trim()) {
      setResults([]);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const feedback = await codeService.getCodeFeedback(codeToAnalyze, lang);
      setResults(feedback);
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze code');
      setResults([{
        id: 'error-1',
        message: err.message || 'Failed to analyze code',
        severity: 'error',
        category: 'other'
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Debounced analyze
  const debouncedAnalyze = useDebounce(analyzeCode, 800);

  // Auto analyze on code change
  const handleCodeChange = (val: string | undefined) => {
    const newCode = val ?? '';
    setCode(newCode);
    if (autoAnalyze) debouncedAnalyze(newCode, language);
  };

  // Manual analyze
  const handleAnalyze = () => {
    analyzeCode(code, language);
  };

  // Language change
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    
    // Load sample snippet if code is empty or a sample from another language
    const currentSample = Object.values(SAMPLE_SNIPPETS).find(sample => code.trim() === sample.trim());
    if (!code.trim() || currentSample) {
      const newSample = SAMPLE_SNIPPETS[newLanguage] || '';
      setCode(newSample);
      if (autoAnalyze) debouncedAnalyze(newSample, newLanguage);
    } else if (autoAnalyze) {
      // Otherwise just analyze current code with new language
      debouncedAnalyze(code, newLanguage);
    }
  };

  // Apply suggestion (replaces error text with suggested fix)
  const handleApplySuggestion = (feedback: AnalysisFeedback) => {
    if (feedback.line && feedback.suggestion && editorRef.current) {
      // This is a simplified implementation - in a real app, you would need more 
      // complex logic to actually modify the right part of the code
      const editor = editorRef.current;
      // For now just navigate to the line
      if (editor.setPosition && editor.revealLineInCenter) {
        editor.setPosition({ lineNumber: feedback.line, column: 1 });
        editor.revealLineInCenter(feedback.line);
        editor.focus();
      }
    }
  };

  // Initial analysis on component mount
  useEffect(() => {
    if (code) {
      debouncedAnalyze(code, language);
    }
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <label className="font-medium">Language:</label>
        <select
          className="border rounded px-2 py-1"
          value={language}
          onChange={handleLanguageChange}
          data-testid="language-selector"
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
            data-testid="auto-analyze-checkbox"
          />
          Auto Analyze
        </label>
        <button
          className="ml-auto px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          onClick={handleAnalyze}
          disabled={loading}
          data-testid="analyze-button"
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
        onEditorMounted={(editor) => { editorRef.current = editor; }}
        data-testid="code-editor"
      />
      
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700" data-testid="error-message">
          <h3 className="font-bold">Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      <AnalysisResult
        feedback={results}
        loading={loading}
        featureCategory="analyze"
        onApplySuggestion={handleApplySuggestion}
        emptyMessage={error ? "Analysis failed" : "Enter some code to analyze"}
      />
    </div>
  );
};

export default CodeAnalyzer;
