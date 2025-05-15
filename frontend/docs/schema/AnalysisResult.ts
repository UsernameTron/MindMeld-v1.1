// AnalysisResult schema
export interface AnalysisResult {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  location?: {
    line: number;
    column: number;
  };
  code?: string;
  suggestion?: string;
}
