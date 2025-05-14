import { authService } from './authService';

export class ApiService {
  private baseUrl: string;
  
  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }
  
  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await authService.fetchWithAuth(`${this.baseUrl}${endpoint}`, {
      ...options,
      method: 'GET'
    });
    
    const contentType = response.headers.get('Content-Type') || '';
    if (!response.ok) {
      // Try to parse error as JSON, but if not possible, throw a generic error
      if (contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.message || `API error: ${response.status}`);
      } else {
        const text = await response.text();
        throw new Error(`API error: ${response.status} - ${text.substring(0, 100)}`);
      }
    }
    // Only parse as JSON if the response is JSON
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      throw new Error(`Expected JSON, got: ${text.substring(0, 100)}`);
    }
    return await response.json();
  }
  
  async post<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> {
    const response = await authService.fetchWithAuth(`${this.baseUrl}${endpoint}`, {
      ...options,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data)
    });
    
    const contentType = response.headers.get('Content-Type') || '';
    if (!response.ok) {
      // Try to parse error as JSON, but if not possible, throw a generic error
      if (contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.message || `API error: ${response.status}`);
      } else {
        const text = await response.text();
        throw new Error(`API error: ${response.status} - ${text.substring(0, 100)}`);
      }
    }
    
    // Only parse as JSON if the response is JSON
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      throw new Error(`Expected JSON, got: ${text.substring(0, 100)}`);
    }
    return await response.json();
  }
  
  async put<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> {
    const response = await authService.fetchWithAuth(`${this.baseUrl}${endpoint}`, {
      ...options,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data)
    });
    
    const contentType = response.headers.get('Content-Type') || '';
    if (!response.ok) {
      if (contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.message || `API error: ${response.status}`);
      } else {
        const text = await response.text();
        throw new Error(`API error: ${response.status} - ${text.substring(0, 100)}`);
      }
    }
    
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      throw new Error(`Expected JSON, got: ${text.substring(0, 100)}`);
    }
    return await response.json();
  }
  
  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await authService.fetchWithAuth(`${this.baseUrl}${endpoint}`, {
      ...options,
      method: 'DELETE'
    });
    
    const contentType = response.headers.get('Content-Type') || '';
    if (!response.ok) {
      if (contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.message || `API error: ${response.status}`);
      } else {
        const text = await response.text();
        throw new Error(`API error: ${response.status} - ${text.substring(0, 100)}`);
      }
    }
    
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      throw new Error(`Expected JSON, got: ${text.substring(0, 100)}`);
    }
    return await response.json();
  }
}

// Export a default instance for convenience
export const apiService = new ApiService();
