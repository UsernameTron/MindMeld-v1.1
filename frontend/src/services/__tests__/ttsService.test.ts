import { vi, describe, it, expect, beforeEach, type Mock } from 'vitest';
import { apiClient } from '../api/apiClient';
import { createTTSService } from '../ttsService';
import { cacheAudio, getCachedAudio } from '../ttsCache';

describe('ttsService', () => {
  const mockApiClient = { request: vi.fn() };
  let ttsService: ReturnType<typeof createTTSService>;

  beforeEach(() => {
    vi.clearAllMocks();
    ttsService = createTTSService(mockApiClient as any);
  });

  it.skip('should convert text to speech successfully', async () => {
    const mockResponse = {
      audio_url: 'https://example.com/audio.mp3',
      duration: 2.5,
      character_count: 10
    };
    (mockApiClient.request as unknown as Mock).mockResolvedValueOnce(mockResponse);

    const result = await ttsService.convertTextToSpeech('Hello world', {
      voice: 'nova',
      model: 'tts-1'
    });

    expect(mockApiClient.request).toHaveBeenCalledWith('/api/tts', {
      method: 'POST',
      data: {
        text: 'Hello world',
        voice: 'nova',
        model: 'tts-1',
        speed: 1.0
      }
    });
    expect(result).toEqual({
      audioUrl: 'https://example.com/audio.mp3',
      duration: 2.5,
      characterCount: 10
    });
  });

  it('should handle errors properly', async () => {
    const mockError = new Error('API error');
    (mockApiClient.request as unknown as Mock).mockRejectedValueOnce(mockError);

    await expect(ttsService.convertTextToSpeech('Hello world', {
      voice: 'nova',
      model: 'tts-1'
    })).rejects.toThrow('TTS error during convertTextToSpeech: API error');
  });
});

const testText = 'Hello world';
const testOptions = { voice: 'alloy' as const, model: 'tts-1' as const, speed: 1.0 };
const mockAudioUrl = 'https://audio.example.com/audio.mp3';
const mockAudioBlob = new Blob(['audio'], { type: 'audio/mpeg' });

vi.stubGlobal('fetch', vi.fn(async (url) => {
  if (url === mockAudioUrl) {
    return { blob: async () => mockAudioBlob };
  }
  throw new Error('Not found');
}));

describe('ttsService (with caching and rate limit)', () => {
  const mockApiClient = { request: vi.fn() };
  const ttsService = createTTSService(mockApiClient as any);

  it.skip('returns cached audio if available', async () => {
    const hash = btoa(unescape(encodeURIComponent(testText + JSON.stringify(testOptions))));
    await cacheAudio(hash, mockAudioBlob);
    const result = await ttsService.convertTextToSpeech(testText, testOptions);
    expect(result.audioUrl.startsWith('blob:')).toBe(true);
    expect(result.characterCount).toBe(testText.length);
  });

  it.skip('fetches and caches audio if not cached', async () => {
    mockApiClient.request.mockResolvedValueOnce({
      data: {
        audio_url: mockAudioUrl,
        duration: 1.23,
        character_count: testText.length
      }
    });
    const result = await ttsService.convertTextToSpeech('New text', { ...testOptions, voice: 'alloy' });
    expect(result.audioUrl).toBe(mockAudioUrl);
    expect(result.duration).toBe(1.23);
    expect(result.characterCount).toBe('New text'.length);
  });

  it('throws on rate limit (429)', async () => {
    mockApiClient.request.mockRejectedValueOnce({ response: { status: 429 } });
    await expect(ttsService.convertTextToSpeech('fail', testOptions)).rejects.toThrow('Rate limited by OpenAI API');
  });
});
