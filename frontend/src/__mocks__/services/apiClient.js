// src/__mocks__/services/apiClient.js
export const apiClient = {
  request: vi.fn(),
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
};
export default { apiClient };
