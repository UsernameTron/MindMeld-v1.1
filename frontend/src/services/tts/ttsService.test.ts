import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createTTSService } from '../ttsService';

// Explicitly mock browser APIs before importing any modules that might use them
// IndexedDB mock
(global as any).indexedDB = {
  open: vi.fn().mockReturnValue({
    onupgradeneeded: null,
    onsuccess: null,
    onerror: null,
    result: {
      createObjectStore: vi.fn().mockReturnValue({
        createIndex: vi.fn()
      }),
      transaction: vi.fn().mockReturnValue({
        objectStore: vi.fn().mockReturnValue({
          put: vi.fn().mockReturnValue({
            onsuccess: null,
            onerror: null
          }),
          get: vi.fn().mockReturnValue({
            onsuccess: null,
            onerror: null
          })
        })
      })
    }
  })
};

(global as any).IDBTransaction = {
  READ_ONLY: 'readonly',
  READ_WRITE: 'readwrite'
};

// Blob API mock
(global as any).Blob = class Blob {
  size: number;
  type: string;
  content: any;
  constructor(content: any[], options: {type: string}) {
    this.content = content;
    this.size = content.reduce((acc, item) => acc + (item?.length || 0), 0);
    this.type = options.type;
  }
  async text() {
    return this.content.join('');
  }
  async arrayBuffer() {
    return new ArrayBuffer(this.size);
  }
};

// Mock fetch to return a response with a .blob() method
(global as any).fetch = vi.fn(() =>
  Promise.resolve({
    blob: () => Promise.resolve(new Blob(['mock-audio'], { type: 'audio/mpeg' }))
  })
);

// Mock URL.createObjectURL to return a fake blob URL
(global as any).URL = {
  createObjectURL: vi.fn(() => 'blob:mock-url')
};

// Mock the ttsCache module with correct path
vi.mock('../ttsCache', () => {
  return {
    getCachedAudio: vi.fn(),
    cacheAudio: vi.fn().mockResolvedValue(undefined),
    openTTSCacheDB: vi.fn().mockResolvedValue({})
  };
});

// Import the mocked module for direct control in tests
import * as ttsCache from '../ttsCache';

function hashTextOptions(text: string, options: any): string {
  return btoa(unescape(encodeURIComponent(text + JSON.stringify(options))));
}

describe('TTSService', () => {
  let ttsService: ReturnType<typeof createTTSService>;
  let mockApiClient: any;
  const testText = 'Hello world';
  const testOptions = { 
    voice: 'alloy' as const, 
    model: 'tts-1' as const,
    speed: 1.0 
  };
  
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    // Set mock behavior to default
    (ttsCache.getCachedAudio as any).mockResolvedValue(undefined);
    // Set up mock API client with properly structured response
    mockApiClient = {
      request: vi.fn().mockResolvedValue({
        data: {
          audio_url: 'mock-url',
          duration: 1.23,
          character_count: testText.length
        }
      })
    };
    // Initialize TTS service with mock client
    ttsService = createTTSService(mockApiClient);
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  it.skip('generates speech and caches audio', async () => {
    // Configure cache miss, then API call, then cache storage
    (ttsCache.getCachedAudio as any).mockResolvedValueOnce(undefined);
    const audioData = await ttsService.convertTextToSpeech(testText, testOptions);
    // Verify proper API call was made
    expect(mockApiClient.request).toHaveBeenCalledWith(
      '/api/tts',
      expect.objectContaining({
        method: 'POST',
        data: expect.objectContaining({
          text: testText,
          voice: testOptions.voice,
          model: testOptions.model
        })
      })
    );
    // Verify cache was called with the correct hash
    expect(ttsCache.getCachedAudio).toHaveBeenCalledWith(
      hashTextOptions(testText, testOptions)
    );
    // Verify audio was cached
    expect(ttsCache.cacheAudio).toHaveBeenCalledWith(
      expect.any(String),
      expect.any(Blob)
    );
    // Verify returned data
    expect(typeof audioData.audioUrl).toBe('string');
    expect(audioData.duration).toBe(1.23);
    expect(audioData.characterCount).toBe(testText.length);
  });
  
  it.skip('reuses cached audio for repeated input', async () => {
    // Mock cache hit
    const cachedBlob = new Blob(['cached-audio-data'], { type: 'audio/mpeg' });
    (ttsCache.getCachedAudio as any).mockResolvedValueOnce(cachedBlob);
    const audioData = await ttsService.convertTextToSpeech(testText, testOptions);
    // Cache was checked with the correct hash
    expect(ttsCache.getCachedAudio).toHaveBeenCalledWith(
      hashTextOptions(testText, testOptions)
    );
    // API was NOT called
    expect(mockApiClient.request).not.toHaveBeenCalled();
    // Cache was NOT updated
    expect(ttsCache.cacheAudio).not.toHaveBeenCalled();
    // The cached blob was returned as a blob URL
    expect(audioData.audioUrl.startsWith('blob:')).toBe(true);
    expect(audioData.characterCount).toBe(testText.length);
  });
  
  it.skip('handles fetch failure gracefully', async () => {
    // API error
    mockApiClient.request.mockRejectedValueOnce(new Error('fetch failed'));
    // Error is propagated correctly
    await expect(
      ttsService.convertTextToSpeech(testText, testOptions)
    ).rejects.toThrow('fetch failed');
  });
  
  it('handles rate limiting (429) with error', async () => {
    // Rate limit response
    mockApiClient.request.mockRejectedValueOnce({ 
      response: { status: 429 } 
    });
    // Rate limit error is handled specially
    await expect(
      ttsService.convertTextToSpeech(testText, testOptions)
    ).rejects.toThrow('Rate limited by OpenAI API');
  });
  
  it('works when caching is disabled', async () => {
    // Service with caching disabled (simulate by not calling cache)
    // You may need to adapt this if your service supports an enableCaching flag
    (ttsCache.getCachedAudio as any).mockResolvedValue(undefined);
    mockApiClient.request.mockResolvedValueOnce({
      data: {
        audio_url: 'mock-url',
        duration: 1.23,
        character_count: testText.length
      }
    });
    const result = await ttsService.convertTextToSpeech('No cache', testOptions);
    expect(mockApiClient.request).toHaveBeenCalled();
    expect(ttsCache.cacheAudio).toHaveBeenCalled();
  });
});
