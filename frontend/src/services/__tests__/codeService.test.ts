import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createCodeService } from '../codeService';

const mockApiClient = {
  post: vi.fn(),
};

describe('codeService (DI)', () => {
  let codeService: ReturnType<typeof createCodeService>;

  beforeEach(() => {
    mockApiClient.post.mockReset();
    codeService = createCodeService(mockApiClient);
    // Clear cache
    // @ts-ignore
    if (codeService.__cache) codeService.__cache.clear();
  });

  it('analyzeCode returns analysis result', async () => {
    const mockResult = { issues: [], complexity_score: 1, optimization_suggestions: [], performance_issues: [], language: 'js', summary: 'ok' };
    mockApiClient.post.mockResolvedValueOnce({ data: mockResult });
    const result = await codeService.analyzeCode('code', 'js');
    expect(mockApiClient.post).toHaveBeenCalledWith('/code/analyze', { code: 'code', language: 'js' });
    expect(result).toEqual(mockResult);
  });

  it('analyzeCode throws on error', async () => {
    mockApiClient.post.mockRejectedValueOnce(new Error('fail'));
    await expect(codeService.analyzeCode('bad', 'js')).rejects.toThrow('fail');
  });
});
