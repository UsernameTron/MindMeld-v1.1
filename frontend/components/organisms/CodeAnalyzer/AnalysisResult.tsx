import React, { useState } from 'react';

/**
 * Interfaces for code analysis result data
 */
export interface AnalysisSummary {
  score: number; // 0-100
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  description: string;
}

export interface ComplexityMetrics {
  cyclomatic: number;
  linesOfCode: number;
  functions: number;
  maintainability: number; // 0-100
}

export type IssueSeverity = 'error' | 'warning' | 'info';

export interface AnalysisIssue {
  id: string;
  message: string;
  severity: IssueSeverity;
  line?: number;
  suggestion?: string;
}

export interface OptimizationSuggestion {
  id: string;
  title: string;
  description: string;
}

export interface AnalysisResultData {
  summary: AnalysisSummary;
  complexity: ComplexityMetrics;
  issues: AnalysisIssue[];
  suggestions: OptimizationSuggestion[];
}

export interface AnalysisResultProps {
  data: AnalysisResultData | null;
  loading?: boolean;
  error?: string;
  theme?: 'light' | 'dark';
}

/**
 * AnalysisResult displays code quality metrics, issues, and suggestions.
 * - Supports light/dark themes via CSS variables
 * - Accessible (ARIA, keyboard navigation, color contrast)
 * - Expand/collapse sections for issues and suggestions
 */
export const AnalysisResult: React.FC<AnalysisResultProps> = ({ data, loading, error, theme = 'light' }) => {
  const [issuesOpen, setIssuesOpen] = useState(true);
  const [suggestionsOpen, setSuggestionsOpen] = useState(true);

  if (loading) {
    return <div role="status" aria-busy="true" className="analysis-result__loading">Analyzing code...</div>;
  }
  if (error) {
    return <div role="alert" className="analysis-result__error">{error}</div>;
  }
  if (!data) {
    return <div className="analysis-result__empty">No analysis results to display.</div>;
  }

  const { summary, complexity, issues, suggestions } = data;

  return (
    <section
      className={`analysis-result analysis-result--${theme}`}
      aria-label="Code analysis results"
      tabIndex={0}
    >
      <header className="analysis-result__header">
        <h2>Code Quality Summary</h2>
        <div className="analysis-result__score" aria-label={`Score: ${summary.score}, Grade: ${summary.grade}`}>
          <span className={`analysis-result__grade analysis-result__grade--${summary.grade.toLowerCase()}`}>{summary.grade}</span>
          <span className="analysis-result__score-value">{summary.score}/100</span>
        </div>
        <p className="analysis-result__description">{summary.description}</p>
      </header>
      <section className="analysis-result__complexity" aria-label="Complexity metrics">
        <h3>Complexity Metrics</h3>
        <ul>
          <li><strong>Cyclomatic:</strong> {complexity.cyclomatic}</li>
          <li><strong>Lines of Code:</strong> {complexity.linesOfCode}</li>
          <li><strong>Functions:</strong> {complexity.functions}</li>
          <li><strong>Maintainability:</strong> {complexity.maintainability}/100</li>
        </ul>
      </section>
      <section className="analysis-result__issues" aria-label="Code issues">
        <button
          className="analysis-result__toggle"
          aria-expanded={issuesOpen}
          aria-controls="issues-list"
          onClick={() => setIssuesOpen(o => !o)}
        >
          {issuesOpen ? 'Hide Issues' : `Show Issues (${issues.length})`}
        </button>
        {issuesOpen && (
          <ul id="issues-list" className="analysis-result__issues-list">
            {issues.length === 0 ? (
              <li>No issues found 🎉</li>
            ) : issues.map(issue => (
              <li key={issue.id} className={`analysis-result__issue analysis-result__issue--${issue.severity}`}
                  tabIndex={0} aria-label={`${issue.severity} at line ${issue.line || 'unknown'}: ${issue.message}`}
              >
                <span className={`analysis-result__severity analysis-result__severity--${issue.severity}`}
                      aria-label={issue.severity} />
                <span className="analysis-result__issue-message">{issue.message}</span>
                {issue.line && <span className="analysis-result__issue-line">(Line {issue.line})</span>}
                {issue.suggestion && <span className="analysis-result__issue-suggestion">Suggestion: {issue.suggestion}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
      <section className="analysis-result__suggestions" aria-label="Optimization suggestions">
        <button
          className="analysis-result__toggle"
          aria-expanded={suggestionsOpen}
          aria-controls="suggestions-list"
          onClick={() => setSuggestionsOpen(o => !o)}
        >
          {suggestionsOpen ? 'Hide Suggestions' : `Show Suggestions (${suggestions.length})`}
        </button>
        {suggestionsOpen && (
          <ul id="suggestions-list" className="analysis-result__suggestions-list">
            {suggestions.length === 0 ? (
              <li>No suggestions at this time.</li>
            ) : suggestions.map(s => (
              <li key={s.id} className="analysis-result__suggestion" tabIndex={0}>
                <strong>{s.title}</strong>: {s.description}
              </li>
            ))}
          </ul>
        )}
      </section>
    </section>
  );
};

export default AnalysisResult;
