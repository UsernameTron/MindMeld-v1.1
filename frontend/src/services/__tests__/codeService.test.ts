import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createCodeService, validateAnalysisResult } from '../codeService';

const mockApiClient = {
  request: vi.fn(),
};

describe('codeService (DI)', () => {
  let codeService: ReturnType<typeof createCodeService>;

  beforeEach(() => {
    mockApiClient.request.mockReset();
    codeService = createCodeService(mockApiClient);
    // Clear cache
    // @ts-ignore
    if (codeService.__cache) codeService.__cache.clear();
  });

  describe('analyzeCode', () => {
    it('calls apiClient.request with correct parameters', async () => {
      const mockResponse = {
        summary: 'Analysis complete',
        issues: [{ line: 1, column: 1, message: 'Test issue', severity: 'info' }],
        complexity_score: 1,
        optimization_suggestions: [],
        performance_issues: [],
        language: 'javascript',
      };
      mockApiClient.request.mockResolvedValue(mockResponse);
      const code = 'const x = 1;';
      const language = 'javascript';
      const options = { includeLinting: true };
      const result = await codeService.analyzeCode(code, language, options);
      expect(mockApiClient.request).toHaveBeenCalledWith('/api/analyze', {
        method: 'POST',
        data: { code, language, includeLinting: true },
      });
      expect(result).toEqual(mockResponse);
    });

    it('analyzeCode returns analysis result', async () => {
      const mockResult = { issues: [], complexity_score: 1, optimization_suggestions: [], performance_issues: [], language: 'js', summary: 'ok' };
      mockApiClient.request.mockResolvedValueOnce({ data: mockResult });
      const result = await codeService.analyzeCode('code', 'js');
      expect(mockApiClient.request).toHaveBeenCalledWith('/api/analyze', {
        method: 'POST',
        data: { code: 'code', language: 'js' }
      });
      expect(result).toEqual({ data: mockResult });
    });

    it('analyzeCode throws on error', async () => {
      mockApiClient.request.mockRejectedValueOnce(new Error('fail'));
      await expect(codeService.analyzeCode('bad', 'js')).rejects.toThrow('fail');
    });
  });

  describe('validateAnalysisResult', () => {
    it('validates a correct analysis result', () => {
      const validResult = {
        id: '1',
        message: 'Test message',
        severity: 'error',
        category: 'bug',
      };
      expect(validateAnalysisResult(validResult)).toBe(true);
    });
    it('returns false for invalid analysis result', () => {
      const invalidResult = {
        summary: 'Analysis complete',
        // Missing required fields
      };
      expect(validateAnalysisResult(invalidResult)).toBe(false);
    });
  });
});
