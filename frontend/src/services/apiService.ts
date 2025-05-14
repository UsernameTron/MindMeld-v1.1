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
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
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
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
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
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  }
  
  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await authService.fetchWithAuth(`${this.baseUrl}${endpoint}`, {
      ...options,
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  }
}

// Export a default instance for convenience
export const apiService = new ApiService();
