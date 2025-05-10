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
  return {
    async analyzeCode(code: string, language?: string): Promise<CodeAnalysisResult> {
      const response = await apiClient.post('/code/analyze', {
        code,
        language,
      });
      return response.data;
    },
  };
}
