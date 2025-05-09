import { apiClient } from './apiClient';

// Export both the class and the function for compatibility
export class DataService {
  async fetchData() {
    const { data } = await apiClient.get<{ value: string }>('/data');
    return data.value;
  }
}

// Create an instance and export the fetchData function directly
export const dataService = new DataService();

export async function fetchData(): Promise<{ value: string }> {
  const { data } = await apiClient.get<{ value: string }>('/data');
  return data;
}
