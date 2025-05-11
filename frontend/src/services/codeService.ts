import type { SupportedLanguage } from '../components/CodeEditor/CodeEditor';
import type { AnalysisFeedback } from '../components/AnalysisResult/AnalysisResult';

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
    async analyzeCode(code: string, language?: string): Promise<CodeAnalysisResult> {
      const response = await apiClient.post('/code/analyze', {
        code,
        language,
      });
      return response.data;
    },
  };

  // Expose cache for test clearing
  (codeService as any).__cache = cache;

  return codeService;
}
