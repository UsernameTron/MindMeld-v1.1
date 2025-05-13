import { apiClient } from './api/apiClient';
import { ServiceError, handleServiceError } from './errors';
import { cacheAudio, getCachedAudio } from './ttsCache';

export interface TTSOptions {
  voice: 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer';
  model: 'tts-1' | 'tts-1-hd';
  speed?: number;
}

export interface TTSResult {
  audioUrl: string;
  duration: number;
  characterCount: number;
}

function hashTextOptions(text: string, options: TTSOptions): string {
  // Simple hash for demo; replace with a robust hash in production
  return btoa(unescape(encodeURIComponent(text + JSON.stringify(options))));
}

export function createTTSService(client = apiClient) {
  return {
    async convertTextToSpeech(text: string, options: TTSOptions): Promise<TTSResult> {
      const hash = hashTextOptions(text, options);
      // Try cache first
      const cached = await getCachedAudio(hash);
      if (cached) {
        return {
          audioUrl: URL.createObjectURL(cached),
          duration: 0, // Optionally store duration in cache
          characterCount: text.length
        };
      }
      try {
        const response = await client.request<{
          audio_url: string;
          duration: number;
          character_count: number;
        }>('/api/tts', {
          method: 'POST',
          data: { 
            text, 
            voice: options.voice,
            model: options.model,
            speed: options.speed || 1.0,
          }
        });
        // Axios responses have data property, cast to expected type
        const { audio_url, duration, character_count } = response.data as {
          audio_url: string;
          duration: number;
          character_count: number;
        };
        // Fetch audio blob and cache it
        const audioResp = await fetch(audio_url);
        const audioBlob = await audioResp.blob();
        await cacheAudio(hash, audioBlob);
        return {
          audioUrl: audio_url,
          duration,
          characterCount: character_count
        };
      } catch (error: any) {
        if (error?.response?.status === 429) {
          // Rate limit handling: throw special error or trigger retry logic
          throw new ServiceError('TTS', 'convertTextToSpeech', 'Rate limited by OpenAI API', error);
        }
        throw handleServiceError('TTS', 'convertTextToSpeech', error);
      }
    }
  };
}

export type TTSService = ReturnType<typeof createTTSService>;
