import axios from 'axios';
import { ServiceError, handleServiceError } from './errors';

// Type definitions
export type FeedbackSeverity = 'info' | 'warning' | 'error';
export type FeedbackCategory = 'style' | 'bug' | 'performance' | 'security' | 'best-practice' | 'other';
export type SupportedLanguage = 'javascript' | 'typescript' | 'python' | 'java' | 'go' | 'csharp';

export interface LanguageOption {
  id: string;
  name: string;
}

export interface AnalysisFeedbackItem {
  id: string;
  message: string;
  severity: FeedbackSeverity;
  category: FeedbackCategory;
  line?: number;
  suggestion?: string;
  details?: string;
}

export interface AnalysisRequest {
  code: string;
  language: string;
  options?: Record<string, any>;
}

// Service implementation
export function createAnalysisService(apiClient: any) {
  const SERVICE_NAME = 'AnalysisService';
  
  return {
    async analyzeCode(request: AnalysisRequest): Promise<AnalysisFeedbackItem[]> {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
          throw new ServiceError(SERVICE_NAME, 'analyzeCode', 'Authentication token not found');
        }
        
        const { data } = await apiClient.request('/api/analyze', {
          method: 'POST',
          data: {
            code: request.code,
            language: request.language,
            ...request.options
          },
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        
        // Validate response format
        if (!Array.isArray(data)) {
          throw new ServiceError(SERVICE_NAME, 'analyzeCode', 'Invalid response format: expected an array');
        }
        
        return data;
      } catch (error) {
        throw handleServiceError(SERVICE_NAME, 'analyzeCode', error);
      }
    },
    
    async getSupportedLanguages(): Promise<LanguageOption[]> {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
          throw new ServiceError(SERVICE_NAME, 'getSupportedLanguages', 'Authentication token not found');
        }
        
        const { data } = await apiClient.request('/api/analyze/languages', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        
        // Validate response format
        if (!Array.isArray(data)) {
          // Fallback languages in case of error
          console.error('Invalid language options response format');
          return [
            { id: 'javascript', name: 'JavaScript' },
            { id: 'typescript', name: 'TypeScript' },
            { id: 'python', name: 'Python' }
          ];
        }
        
        return data;
      } catch (error) {
        // Return fallback languages in case of service error
        console.error('Error fetching supported languages:', error);
        return [
          { id: 'javascript', name: 'JavaScript' },
          { id: 'typescript', name: 'TypeScript' },
          { id: 'python', name: 'Python' }
        ];
      }
    }
  };
}

// Default instance with axios
const defaultApiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth interceptor
defaultApiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Export a default instance
export const analysisService = createAnalysisService(defaultApiClient);