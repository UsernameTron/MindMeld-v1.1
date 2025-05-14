import { authService } from './authService';

/**
 * Service for making requests to external APIs via our proxy
 */
export const externalService = {
  /**
   * Make a request to the LibreChat API via our proxy
   */
  librechat: {
    /**
     * Send a request to LibreChat API
     * @param endpoint The LibreChat API endpoint
     * @param options Request options
     * @returns Promise with the response data
     */
    request: async <T>(
      endpoint: string, 
      options: RequestInit = {}
    ): Promise<T> => {
      try {
        // Use the auth service's fetchWithAuth to handle authentication
        const response = await authService.fetchWithAuth(
          `/api/proxy/librechat/${endpoint}`,
          options
        );
        
        if (!response.ok) {
          const error = await response.json().catch(() => ({ message: 'Unknown error' }));
          throw new Error(error.message || `Request failed with status ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('LibreChat request error:', error);
        throw error;
      }
    },
    
    /**
     * Chat with LibreChat
     * @param message The message to send
     * @param options Additional options
     * @returns Promise with the response
     */
    chat: async (message: string, options: any = {}) => {
      return externalService.librechat.request('chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          ...options,
        }),
      });
    },
    
    /**
     * Get available models from LibreChat
     * @returns Promise with available models
     */
    getModels: async () => {
      return externalService.librechat.request('models', {
        method: 'GET',
      });
    },
  },
  
  /**
   * Generic proxy request handler - can be used for any service
   * @param service The service name configured in the proxy
   * @param endpoint The API endpoint
   * @param options Request options
   * @returns Promise with the response data
   */
  proxyRequest: async <T>(
    service: string,
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    try {
      // Use the auth service's fetchWithAuth to handle authentication
      const response = await authService.fetchWithAuth(
        `/api/proxy/${service}/${endpoint}`,
        options
      );
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(error.message || `Request failed with status ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`${service} request error:`, error);
      throw error;
    }
  },
};