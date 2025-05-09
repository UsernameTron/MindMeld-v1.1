import { apiClient } from './apiClient';

export class DataService {
  async fetchData() {
    const { data } = await apiClient.get<{ value: string }>('/data');
    return data.value;
  }
}
