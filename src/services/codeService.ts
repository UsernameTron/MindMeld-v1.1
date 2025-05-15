import axios from 'axios';

// --- TypeScript interfaces for API integration ---
export interface AnalyzeCodeRequest {
  code: string;
  language: string;
}

export interface AnalyzeCodeResponse {
  summary: {
    score: number;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    description: string;
  };
  complexity: {
    cyclomatic: number;
    linesOfCode: number;
    functions: number;
    maintainability: number;
  };
  issues: Array<{
    id: string;
    message: string;
    severity: 'error' | 'warning' | 'info';
    line?: number;
    suggestion?: string;
  }>;
  suggestions: Array<{
    id: string;
    title: string;
    description: string;
  }>;
}

export interface AnalyzeCodeError {
  message: string;
  status?: number;
}

// --- API call function ---
export async function analyzeCode(
  payload: AnalyzeCodeRequest
): Promise<AnalyzeCodeResponse> {
  try {
    const res = await axios.post<AnalyzeCodeResponse>('/analyze/code', payload);
    return res.data;
  } catch (err: any) {
    let message = 'Unknown error';
    let status;
    if (err.response) {
      message = err.response.data?.message || err.response.statusText;
      status = err.response.status;
    } else if (err.message) {
      message = err.message;
    }
    throw { message, status } as AnalyzeCodeError;
  }
}
