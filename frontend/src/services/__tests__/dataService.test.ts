import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createDataService } from '../dataService';

const mockApiClient = {
  get: vi.fn(),
};

describe('dataService (DI)', () => {
  let dataService: ReturnType<typeof createDataService>;

  beforeEach(() => {
    mockApiClient.get.mockReset();
    dataService = createDataService(mockApiClient);
  });

  it('fetchData returns value from API', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: { value: 'hello' } });
    const result = await dataService.fetchData();
    expect(mockApiClient.get).toHaveBeenCalledWith('/api/data');
    expect(result).toEqual({ value: 'hello' });
  });

  it('fetchData throws on error', async () => {
    mockApiClient.get.mockRejectedValueOnce(new Error('fail'));
    await expect(dataService.fetchData()).rejects.toThrow('fail');
  });
});
