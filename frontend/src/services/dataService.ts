import axios from 'axios';

// Export both the class and the function for compatibility
export function createDataService(apiClient: any) {
  return {
    async fetchData() {
      try {
        const { data } = await apiClient.get('/api/data');
        return data;
      } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
      }
    },
  };
}

// Create a default instance with axios
export const dataService = createDataService(axios);

// For compatibility with existing code
export const fetchData = () => dataService.fetchData();
