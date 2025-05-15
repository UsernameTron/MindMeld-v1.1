import type { SupportedLanguage } from '../components/CodeEditor/CodeEditor';
import type { AnalysisFeedback, FeedbackSeverity, FeedbackCategory } from '@components/ui/organisms/AnalysisResult/AnalysisResult';
import Ajv from 'ajv';
import reviewSchema from '../../../schemas/review.schema.json';

export interface CodeQualityIssue {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
  details?: string;
}

export interface CodeAnalysisResult {
  issues: CodeQualityIssue[];
  complexity_score: number;
  optimization_suggestions: string[];
  performance_issues: Array<Record<string, string>>;
  language: string;
  summary: string;
}

// Maps API response severity to UI component severity
const mapSeverity = (severity: string): FeedbackSeverity => {
  if (severity === 'error') return 'error';
  if (severity === 'warning') return 'warning';
  return 'info';
};

// Maps API response issue types to UI component categories
const mapCategory = (type: string): FeedbackCategory => {
  const mapping: Record<string, FeedbackCategory> = {
    'performance': 'performance',
    'security': 'security',
    'style': 'style',
    'bug': 'bug',
    'best-practice': 'best-practice'
  };
  return mapping[type] || 'other';
};

// Converts API response to UI-compatible feedback format
export function convertToAnalysisFeedback(result: CodeAnalysisResult): AnalysisFeedback[] {
  const feedback: AnalysisFeedback[] = [];
  
  // Convert direct issues
  if (result.issues && Array.isArray(result.issues)) {
    result.issues.forEach((issue, index) => {
      feedback.push({
        id: `issue-${index}`,
        message: issue.message,
        severity: mapSeverity(issue.severity),
        category: 'bug',
        line: issue.line,
        suggestion: issue.suggestion,
        details: issue.details
      });
    });
  }
  
  // Convert optimization suggestions
  if (result.optimization_suggestions && Array.isArray(result.optimization_suggestions)) {
    result.optimization_suggestions.forEach((suggestion, index) => {
      feedback.push({
        id: `opt-${index}`,
        message: suggestion,
        severity: 'info',
        category: 'performance'
      });
    });
  }
  
  // Add performance issues
  if (result.performance_issues && Array.isArray(result.performance_issues)) {
    result.performance_issues.forEach((issue, index) => {
      feedback.push({
        id: `perf-${index}`,
        message: issue.message || Object.values(issue).join(': '),
        severity: 'warning',
        category: 'performance',
        details: Object.entries(issue)
          .filter(([key]) => key !== 'message')
          .map(([key, value]) => `${key}: ${value}`)
          .join('\n')
      });
    });
  }
  
  // If no issues found, add a positive feedback message
  if (feedback.length === 0) {
    feedback.push({
      id: 'no-issues',
      message: `No issues found in your ${result.language} code!`,
      severity: 'info',
      category: 'best-practice'
    });
  }
  
  return feedback;
}

export function createCodeService(apiClient: any) {
  const CACHE_TTL = 30 * 1000; // 30 seconds
  const cache = new Map<string, { result: AnalysisFeedback[]; timestamp: number }>();

  const codeService = {
    /**
     * Analyzes code and returns detailed feedback
     * @param code The source code to analyze
     * @param language The programming language of the code
     * @param options Additional options for analysis
     * @returns Detailed code analysis results
     */
    async analyzeCode(code: string, language?: string, options?: Record<string, any>): Promise<CodeAnalysisResult> {
      try {
        const response = await apiClient.request('/api/analyze/code', {
          method: 'POST',
          data: { code, language, ...options }
        });
        return response.data as CodeAnalysisResult;
      } catch (error) {
        console.error('Failed to analyze code:', error);
        throw new Error('Code analysis failed. Please try again later.');
      }
    },
    
    /**
     * Analyzes code and returns UI-ready feedback items
     * @param code The source code to analyze
     * @param language The programming language of the code
     * @param options Additional options for analysis
     * @returns Analysis feedback formatted for UI components
     */
    async getCodeFeedback(code: string, language?: string, options?: Record<string, any>): Promise<AnalysisFeedback[]> {
      // Generate cache key based on inputs
      const cacheKey = JSON.stringify({ code, language, options });
      
      // Check cache first
      const cached = cache.get(cacheKey);
      const now = Date.now();
      if (cached && now - cached.timestamp < CACHE_TTL) {
        return cached.result;
      }
      
      try {
        // If empty code, return empty results
        if (!code || code.trim() === '') {
          return [];
        }
        
        const result = await this.analyzeCode(code, language, options);
        
        // Validate response
        if (!validateAnalysisResult(result)) {
          console.warn('Invalid analysis result received:', result);
          throw new Error('Received invalid analysis result from server');
        }
        
        // Convert API response to UI feedback format
        const feedback = convertToAnalysisFeedback(result);
        
        // Cache the result
        cache.set(cacheKey, { result: feedback, timestamp: now });
        
        return feedback;
      } catch (error: any) {
        // Return error as feedback
        const errorFeedback: AnalysisFeedback = {
          id: 'error-1',
          message: error.message || 'Failed to analyze code',
          severity: 'error',
          category: 'other'
        };
        return [errorFeedback];
      }
    }
  };

  // Expose cache for test clearing
  (codeService as any).__cache = cache;

  return codeService;
}

const ajv = new Ajv();
const validateReview = ajv.compile(reviewSchema);

export function validateAnalysisResult(result: any): boolean {
  return validateReview(result) as boolean;
}
