'use client';
import { useState } from 'react';
import type { SupportedLanguage } from '../CodeEditor/CodeEditor';
// import type { AnalysisFeedback } from '@components/ui/organisms/AnalysisResult/AnalysisResult';

export type { SupportedLanguage } from '../CodeEditor/CodeEditor };

export interface UseCodeAnalysis {
  code: string;
  setCode: (code: string) => void;
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  feedback: any[]; // @ts-ignore TEMP for debug
  error: string | null;
  isAnalyzing: boolean;
  analyzeCode: () => void;
  applyFeedbackSuggestion: (feedback: any) => void;
}

const mockAnalyzeCode = (code: string, language: SupportedLanguage): any[] => {
  if (!code.trim()) return [];
  // Simple mock: always return a warning and an info
  return [
    {
      id: '1',
      message: 'Mock: Unused variable',
      severity: 'warning',
      category: 'style',
      line: 2,
      suggestion: 'Remove unused variable',
      details: 'This is a mock warning for demonstration.',
    },
    {
      id: '2',
      message: 'Mock: Consider using const',
      severity: 'info',
      category: 'best-practice',
      line: 1,
    },
  ];
};

export function useCodeAnalysis(initialCode = '', initialLanguage: SupportedLanguage = 'javascript'): UseCodeAnalysis {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState<SupportedLanguage>(initialLanguage);
  const [feedback, setFeedback] = useState<any[]>([]); // @ts-ignore TEMP for debug
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeCode = () => {
    setIsAnalyzing(true);
    setError(null);
    try {
      // Replace with real codeService.analyzeCode in future
      const result = mockAnalyzeCode(code, language);
      setFeedback(result);
    } catch (e: any) {
      setError(e.message || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const applyFeedbackSuggestion = (feedbackItem: any) => {
    // Simple mock: just append suggestion to code
    if (feedbackItem.suggestion) {
      setCode(code + '\n// Suggestion applied: ' + feedbackItem.suggestion);
    }
  };

  return {
    code,
    setCode,
    language,
    setLanguage,
    feedback,
    error,
    isAnalyzing,
    analyzeCode,
    applyFeedbackSuggestion,
  };
}
