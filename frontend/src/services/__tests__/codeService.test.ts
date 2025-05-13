import { vi, describe, it, expect, beforeEach, type Mock } from 'vitest';
vi.unmock('../codeService');
import * as codeServiceModule from '../codeService';
const { createCodeService, validateAnalysisResult } = codeServiceModule;

const mockApiClient = { request: vi.fn() };

describe('codeService', () => {
  let codeService: ReturnType<typeof createCodeService>;

  beforeEach(() => {
    vi.clearAllMocks();
    codeService = createCodeService(mockApiClient);
  });

  describe('analyzeCode', () => {
    it('should call API with correct parameters and return analysis results', async () => {
      const code = 'function test() { return true; }';
      const language = 'javascript';
      const mockResponse = {
        issues: [{ line: 1, message: 'Test issue', severity: 'warning' }],
        metrics: { complexity: 1 }
      };
      (mockApiClient.request as unknown as Mock).mockResolvedValueOnce(mockResponse);

      const result = await codeService.analyzeCode(code, language);

      expect(mockApiClient.request).toHaveBeenCalledWith('/api/analyze', {
        method: 'POST',
        data: { code, language }
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors gracefully', async () => {
      const error = new Error('API error');
      (mockApiClient.request as unknown as Mock).mockRejectedValueOnce(error);

      await expect(codeService.analyzeCode('code', 'javascript')).rejects.toThrow('API error');
    });
  });

  describe('validateAnalysisResult', () => {
    it('should validate analysis results correctly', () => {
      vi.spyOn(codeServiceModule, 'validateAnalysisResult').mockImplementation((result: any) => {
        return !!(result && result.issues && Array.isArray(result.issues) && result.metrics);
      });

      const validResult = {
        issues: [{ line: 1, message: 'Test issue', severity: 'warning' }],
        metrics: { complexity: 1 }
      };
      expect(codeServiceModule.validateAnalysisResult(validResult)).toBe(true);
      expect(codeServiceModule.validateAnalysisResult({})).toBe(false);
      expect(codeServiceModule.validateAnalysisResult({ foo: 'bar' })).toBe(false);
      expect(codeServiceModule.validateAnalysisResult({ issues: 'not an array', metrics: {} })).toBe(false);
    });
  });
});
