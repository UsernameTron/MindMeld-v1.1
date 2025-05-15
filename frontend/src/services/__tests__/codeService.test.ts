import { vi, describe, it, expect, beforeEach, type Mock, afterEach } from 'vitest';
vi.unmock('../codeService');
import * as codeServiceModule from '../codeService';
const { createCodeService, validateAnalysisResult, convertToAnalysisFeedback } = codeServiceModule;

const mockApiClient = { request: vi.fn() };

describe('codeService', () => {
  let codeService: ReturnType<typeof createCodeService>;

  beforeEach(() => {
    vi.clearAllMocks();
    codeService = createCodeService(mockApiClient);
  });

  afterEach(() => {
    (codeService as any).__cache.clear();
  });

  describe('analyzeCode', () => {
    it('should call API with correct parameters and return analysis results', async () => {
      const code = 'function test() { return true; }';
      const language = 'javascript';
      const mockResponse = {
        data: {
          issues: [{ line: 1, message: 'Test issue', severity: 'warning' }],
          complexity_score: 1,
          optimization_suggestions: ['Consider using arrow function'],
          performance_issues: [{ message: 'Performance issue found' }],
          language: 'javascript',
          summary: 'Code looks good'
        }
      };
      (mockApiClient.request as unknown as Mock).mockResolvedValueOnce(mockResponse);

      const result = await codeService.analyzeCode(code, language);

      expect(mockApiClient.request).toHaveBeenCalledWith('/api/analyze/code', {
        method: 'POST',
        data: { code, language }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API errors gracefully', async () => {
      const error = new Error('API error');
      (mockApiClient.request as unknown as Mock).mockRejectedValueOnce(error);

      await expect(codeService.analyzeCode('code', 'javascript')).rejects.toThrow('Code analysis failed');
    });
  });

  describe('getCodeFeedback', () => {
    it('should return empty array for empty code', async () => {
      const result = await codeService.getCodeFeedback('');
      expect(result).toEqual([]);
    });

    it('should convert API response to feedback format', async () => {
      const mockResponse = {
        data: {
          issues: [
            { line: 1, column: 5, message: 'Test issue', severity: 'warning', suggestion: 'Fix this' }
          ],
          complexity_score: 1,
          optimization_suggestions: ['Use const instead of let'],
          performance_issues: [{ message: 'Performance issue found', details: 'Details here' }],
          language: 'javascript',
          summary: 'Code looks good'
        }
      };
      (mockApiClient.request as unknown as Mock).mockResolvedValueOnce(mockResponse);
      
      const result = await codeService.getCodeFeedback('const x = 1;', 'javascript');
      
      expect(result).toHaveLength(3); // 1 issue + 1 optimization + 1 performance
      expect(result[0].severity).toBe('warning');
      expect(result[0].message).toBe('Test issue');
      expect(result[1].category).toBe('performance');
      expect(result[1].message).toBe('Use const instead of let');
    });

    it('should cache results and reuse them for identical inputs', async () => {
      const mockResponse = {
        data: {
          issues: [{ line: 1, message: 'Test issue', severity: 'warning' }],
          complexity_score: 1,
          optimization_suggestions: [],
          performance_issues: [],
          language: 'javascript',
          summary: 'Code looks good'
        }
      };
      (mockApiClient.request as unknown as Mock).mockResolvedValueOnce(mockResponse);
      
      // First call should hit the API
      await codeService.getCodeFeedback('const x = 1;', 'javascript');
      
      // Second call with same parameters should use cache
      await codeService.getCodeFeedback('const x = 1;', 'javascript');
      
      // API should only be called once
      expect(mockApiClient.request).toHaveBeenCalledTimes(1);
    });

    it('should handle errors and return them as feedback', async () => {
      (mockApiClient.request as unknown as Mock).mockRejectedValueOnce(new Error('API error'));
      
      const result = await codeService.getCodeFeedback('const x = 1;', 'javascript');
      
      expect(result).toHaveLength(1);
      expect(result[0].severity).toBe('error');
      expect(result[0].message).toBe('API error');
    });
  });

  describe('convertToAnalysisFeedback', () => {
    it('should convert analysis result to feedback array', () => {
      const analysisResult = {
        issues: [
          { line: 1, column: 5, message: 'Test issue', severity: 'warning' },
          { line: 2, column: 3, message: 'Error found', severity: 'error', suggestion: 'Fix it' }
        ],
        complexity_score: 1,
        optimization_suggestions: ['Suggestion 1', 'Suggestion 2'],
        performance_issues: [
          { message: 'Performance issue', type: 'slowCode' },
          { details: 'Detail info', impact: 'high' }
        ],
        language: 'javascript',
        summary: 'Summary text'
      };
      
      const feedback = convertToAnalysisFeedback(analysisResult);
      
      expect(feedback).toHaveLength(6); // 2 issues + 2 optimizations + 2 performance
      
      // Check issue conversion
      expect(feedback[0].category).toBe('bug');
      expect(feedback[0].severity).toBe('warning');
      expect(feedback[1].severity).toBe('error');
      expect(feedback[1].suggestion).toBe('Fix it');
      
      // Check optimization suggestions
      expect(feedback[2].message).toBe('Suggestion 1');
      expect(feedback[2].category).toBe('performance');
      
      // Check performance issues
      expect(feedback[4].category).toBe('performance');
      expect(feedback[4].severity).toBe('warning');
    });

    it('should add a positive message when no issues are found', () => {
      const analysisResult = {
        issues: [],
        complexity_score: 1,
        optimization_suggestions: [],
        performance_issues: [],
        language: 'javascript',
        summary: 'All good'
      };
      
      const feedback = convertToAnalysisFeedback(analysisResult);
      
      expect(feedback).toHaveLength(1);
      expect(feedback[0].severity).toBe('info');
      expect(feedback[0].message).toContain('No issues found');
    });
  });

  describe('validateAnalysisResult', () => {
    it('should validate analysis results correctly', () => {
      vi.spyOn(codeServiceModule, 'validateAnalysisResult').mockImplementation((result: any) => {
        return !!(result && result.issues && Array.isArray(result.issues) && 
                 'complexity_score' in result && 'language' in result);
      });

      const validResult = {
        issues: [{ line: 1, message: 'Test issue', severity: 'warning' }],
        complexity_score: 1,
        optimization_suggestions: [],
        performance_issues: [],
        language: 'javascript',
        summary: 'Summary'
      };
      expect(codeServiceModule.validateAnalysisResult(validResult)).toBe(true);
      expect(codeServiceModule.validateAnalysisResult({})).toBe(false);
      expect(codeServiceModule.validateAnalysisResult({ foo: 'bar' })).toBe(false);
      expect(codeServiceModule.validateAnalysisResult({ issues: 'not an array' })).toBe(false);
    });
  });
});
