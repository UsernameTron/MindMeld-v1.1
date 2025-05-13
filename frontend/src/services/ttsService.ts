import { ApiClient } from './api/apiClient';
import { ServiceError, handleServiceError } from './errors';

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

export function createTTSService(apiClient: ApiClient) {
  return {
    async convertTextToSpeech(text: string, options: TTSOptions): Promise<TTSResult> {
      try {
        const response = await apiClient.request<{
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

        return {
          audioUrl: response.audio_url,
          duration: response.duration,
          characterCount: response.character_count
        };
      } catch (error) {
        throw handleServiceError('TTS', 'convertTextToSpeech', error);
      }
    }
  };
}

export type TTSService = ReturnType<typeof createTTSService>;
