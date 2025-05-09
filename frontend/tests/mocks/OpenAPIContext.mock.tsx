import React from 'react';
import { OpenAPIContextType } from '../../src/context/OpenAPIContext';
import { OpenAPISpec } from '../../src/utils/openapi';

// Mock OpenAPI specification
export const mockOpenAPISpec: OpenAPISpec = {
  openapi: '3.0.0',
  info: {
    title: 'Mock API',
    version: '1.0.0',
    description: 'Mock OpenAPI specification for testing'
  },
  paths: {
    '/api/items': {
      get: {
        summary: 'Get all items',
        operationId: 'getItems',
        responses: {
          '200': {
            description: 'Successful response',
            content: {
              'application/json': {
                schema: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      id: { type: 'string' },
                      name: { type: 'string' }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
};

// Create a context with the mock value
export const MockOpenAPIContext = React.createContext<OpenAPIContextType>({
  spec: mockOpenAPISpec
});

// Provider component that uses the mock context
export const MockOpenAPIProvider: React.FC<{
  spec?: OpenAPISpec | null;
  children: React.ReactNode;
}> = ({ spec = mockOpenAPISpec, children }) => {
  return (
    <MockOpenAPIContext.Provider value={{ spec }}>
      {children}
    </MockOpenAPIContext.Provider>
  );
};

// Hook for using the mock OpenAPI context
export const useMockOpenAPI = (): OpenAPIContextType => React.useContext(MockOpenAPIContext);
