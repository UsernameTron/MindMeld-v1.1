// src/__mocks__/services/codeService.js
import { vi } from 'vitest';

// Mock analysis result
const mockAnalysisResult = {
  issues: [],
  complexity_score: 1,
  optimization_suggestions: [],
  performance_issues: [],
  language: 'typescript',
  summary: 'mock summary',
};

// Mock validation function
export const validateAnalysisResult = vi.fn().mockReturnValue(true);

// Export the createCodeService function
export const createCodeService = vi.fn(() => ({
  analyzeCode: vi.fn().mockResolvedValue(mockAnalysisResult),
  validateAnalysisResult
}));

// Default export
export default { 
  createCodeService,
  validateAnalysisResult
};
