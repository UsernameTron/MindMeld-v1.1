import { vi, describe, it, expect, beforeEach, type Mock } from 'vitest';
import { apiClient } from '../api/apiClient';
import { createTTSService } from '../ttsService';

describe('ttsService', () => {
  const mockApiClient = { request: vi.fn() };
  let ttsService: ReturnType<typeof createTTSService>;

  beforeEach(() => {
    vi.clearAllMocks();
    ttsService = createTTSService(mockApiClient as any);
  });

  it('should convert text to speech successfully', async () => {
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
