// Export both the class and the function for compatibility
export function createDataService(apiClient: any) {
  return {
    async fetchData() {
      const { data } = await apiClient.get('/data');
      return data.value;
    },
  };
}
