import type { SupportedLanguage } from '../components/CodeEditor/CodeEditor';
import type { AnalysisFeedback } from '../components/AnalysisResult/AnalysisResult';
import Ajv from 'ajv';
import reviewSchema from '../../../schemas/review.schema.json';

export interface CodeQualityIssue {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
}

export interface CodeAnalysisResult {
  issues: CodeQualityIssue[];
  complexity_score: number;
  optimization_suggestions: string[];
  performance_issues: Array<Record<string, string>>;
  language: string;
  summary: string;
}

export function createCodeService(apiClient: any) {
  const CACHE_TTL = 30 * 1000; // 30 seconds
  const cache = new Map<string, { result: AnalysisFeedback[]; timestamp: number }>();

  const codeService = {
    async analyzeCode(code: string, language?: string, options?: Record<string, any>): Promise<CodeAnalysisResult> {
      return apiClient.request('/api/analyze', {
        method: 'POST',
        data: { code, language, ...options }
      }) as Promise<CodeAnalysisResult>;
    },
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
