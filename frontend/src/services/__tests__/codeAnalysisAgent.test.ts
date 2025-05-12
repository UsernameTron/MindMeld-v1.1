import { describe, it, expect, vi } from 'vitest';
import { createCodeService } from '@/services/codeService';

// Mock API response for analysis
const mockAnalysisResponse = {
  data: {
    issues: [
      { line: 1, column: 1, message: 'Test issue', severity: 'warning' }
    ],
    complexity_score: 2,
    optimization_suggestions: ['Use memoization'],
    performance_issues: [{ detail: 'Loop unoptimized' }],
    language: 'typescript',
    summary: 'Test summary',
  }
};

describe('codeService.analyzeCode (mocked)', () => {
  it('returns the expected analysis result from the mock', async () => {
    const mockPost = vi.fn().mockResolvedValue(mockAnalysisResponse);
    const codeService = createCodeService({
      request: (_url: string, opts: any) => mockPost('/api/analyze', opts)
    });

    const result = await codeService.analyzeCode('let x = 1;', 'typescript');

    // Ensure the mock was called with correct params
    expect(mockPost).toHaveBeenCalledWith(
      '/api/analyze',
      { method: 'POST', data: { code: 'let x = 1;', language: 'typescript' } }
    );

    // The service returns the whole mock response (see codeService implementation)
    expect(result).toEqual(mockAnalysisResponse);
    // Optionally, check shape
    expect(result.data).toHaveProperty('issues');
    expect(Array.isArray(result.data.issues)).toBe(true);
    expect(result.data).toHaveProperty('complexity_score');
    expect(result.data).toHaveProperty('optimization_suggestions');
    expect(result.data).toHaveProperty('performance_issues');
    expect(result.data).toHaveProperty('language');
    expect(result.data).toHaveProperty('summary');
  });
});
