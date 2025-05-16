import { describe, it, expect, vi } from 'vitest';
vi.unmock('@/services/codeService');
import { createCodeService } from '@/services/codeService';

// Mock API response for analysis
const mockAnalysisData = {
  issues: [
    { line: 1, column: 1, message: 'Test issue', severity: 'warning' }
  ],
  complexity_score: 2,
  optimization_suggestions: ['Use memoization'],
  performance_issues: [{ detail: 'Loop unoptimized' }],
  language: 'typescript',
  summary: 'Test summary',
};

describe('codeService.analyzeCode (mocked)', () => {
  it('returns the expected analysis result from the mock', async () => {
    // Create a proper mock API client
    const mockApiClient = {
      request: vi.fn().mockResolvedValue(mockAnalysisData)
    };
    // Create service with the mock API client
    const codeService = createCodeService(mockApiClient);
    // Call the service
    const result = await codeService.analyzeCode('let x = 1;', 'typescript');
    // Verify the API client was called correctly
    expect(mockApiClient.request).toHaveBeenCalledWith(
      '/api/analyze/code',
      { method: 'POST', data: { code: 'let x = 1;', language: 'typescript' } }
    );
    // Verify the result
    expect(result).toEqual(mockAnalysisData);
    // Optional shape verification
    expect(result).toHaveProperty('issues');
    expect(Array.isArray(result.issues)).toBe(true);
    expect(result).toHaveProperty('complexity_score');
    expect(result).toHaveProperty('optimization_suggestions');
    expect(result).toHaveProperty('performance_issues');
    expect(result).toHaveProperty('language');
    expect(result).toHaveProperty('summary');
  });
});
