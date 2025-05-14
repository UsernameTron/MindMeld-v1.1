'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Metadata } from 'next';
import CodeEditor from '@/components/ui/organisms/CodeEditor/CodeEditor';
import AnalysisResult from '@/components/ui/organisms/AnalysisResult/AnalysisResult';
import { FeatureErrorBoundary } from '@/components/ui/organisms/FeatureErrorBoundary/FeatureErrorBoundary';
import { ErrorDisplay } from '@/components/ui/molecules/ErrorDisplay';
import { AnalyzerSettings } from '@/components/ui/molecules/AnalyzerSettings';
import { analysisService, type AnalysisFeedbackItem } from '@/services/analysisService';
import { useSettingsContext } from '@/context/SettingsContext';
import { debounce } from 'lodash';
import { metadata } from './metadata';

// This must be set in a separate file as metadata can't be in client components

export default function AnalyzePage() {
  // Get settings from context
  const { settings, updateAnalyzerSettings } = useSettingsContext();
  const { analyzer } = settings;
  
  // State management
  const [code, setCode] = useState(analyzer.initialCode);
  const [feedback, setFeedback] = useState<AnalysisFeedbackItem[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [supportedLanguages, setSupportedLanguages] = useState<{ id: string, name: string }[]>([
    { id: 'javascript', name: 'JavaScript' },
    { id: 'typescript', name: 'TypeScript' },
    { id: 'python', name: 'Python' }
  ]);
  const [isLoadingLanguages, setIsLoadingLanguages] = useState(true);

  // Update code in settings when it changes
  useEffect(() => {
    updateAnalyzerSettings({ initialCode: code });
  }, [code, updateAnalyzerSettings]);

  // Fetch supported languages on component mount
  useEffect(() => {
    async function fetchLanguages() {
      try {
        const languages = await analysisService.getSupportedLanguages();
        setSupportedLanguages(languages);
      } catch (err) {
        console.error('Failed to fetch supported languages:', err);
        // Fallback is already set in the initial state
      } finally {
        setIsLoadingLanguages(false);
      }
    }
    
    fetchLanguages();
  }, []);

  // Handle code analysis
  const handleAnalyze = useCallback(async () => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      console.log('Analyzing code:', { code: code.substring(0, 100) + '...', language: analyzer.language });
      
      const result = await analysisService.analyzeCode({
        code,
        language: analyzer.language,
        options: {
          // Include settings based options
          rulesets: analyzer.rulesets,
          ignoredWarnings: analyzer.customRules.ignoredWarnings,
          ignoredCategories: analyzer.customRules.ignoredCategories
        }
      });
      
      console.log('Analysis result:', result);
      setFeedback(result);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
      setFeedback([]);
    } finally {
      setIsAnalyzing(false);
    }
  }, [code, analyzer]);

  // Set up auto-analyze with debounce
  useEffect(() => {
    if (!analyzer.autoAnalyze) return;
    
    const debouncedAnalyze = debounce(handleAnalyze, analyzer.debounceMs);
    debouncedAnalyze();
    
    return () => {
      debouncedAnalyze.cancel();
    };
  }, [code, analyzer.autoAnalyze, analyzer.debounceMs, handleAnalyze]);

  // Apply feedback suggestion to code
  const handleApplySuggestion = useCallback((feedbackItem: AnalysisFeedbackItem) => {
    if (feedbackItem.suggestion) {
      // This is a simple implementation - in a real world scenario, you'd want to
      // apply the suggestion at the correct position in the code
      setCode(prev => prev + '\n// Applied suggestion: ' + feedbackItem.suggestion);
    }
  }, []);

  // Calculate the editor theme based on settings
  const editorTheme = useCallback(() => {
    if (analyzer.theme === 'system') {
      // Check system preference
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'light';
    }
    return analyzer.theme;
  }, [analyzer.theme]);

  return (
    <FeatureErrorBoundary category="analyze" fallback={<ErrorDisplay severity="error" message="Something went wrong with the code analyzer" title="Analyzer Error" />}>
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold mb-6">Code Analyzer</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Settings sidebar */}
          <div className="lg:col-span-1">
            <AnalyzerSettings
              supportedLanguages={supportedLanguages}
              isLoadingLanguages={isLoadingLanguages}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
            />
          </div>
          
          {/* Main code editor and analysis results */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-md border border-slate-200 dark:border-slate-700 overflow-hidden">
              <CodeEditor
                value={code}
                onChange={(value) => setCode(value || '')}
                language={analyzer.language as any}
                theme={editorTheme() as any}
                height="400px"
                readOnly={isAnalyzing}
              />
            </div>
            
            <div className="bg-white dark:bg-slate-900 rounded-md border border-slate-200 dark:border-slate-700 p-4">
              <AnalysisResult 
                feedback={feedback}
                loading={isAnalyzing}
                emptyMessage={error || (analyzer.autoAnalyze 
                  ? 'Type to trigger automatic analysis...' 
                  : 'No analysis results yet. Click "Analyze Code" to start.')}
                featureCategory="analyze"
                onApplySuggestion={handleApplySuggestion}
              />
            </div>
          </div>
        </div>
      </div>
    </FeatureErrorBoundary>
  );
}