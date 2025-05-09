import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { MockOpenAPIProvider, mockOpenAPISpec } from '../../../tests/mocks/OpenAPIContext.mock';

// Simple component that takes API spec as a prop
const ApiEndpointList = ({ spec }) => {
  if (!spec) {
    return <div data-testid="loading">Loading API specification...</div>;
  }
  
  // Get all endpoint paths
  const paths = Object.keys(spec.paths || {});
  
  return (
    <div>
      <h2>API Endpoints</h2>
      <ul data-testid="endpoint-list">
        {paths.map(path => (
          <li key={path} data-testid="endpoint">{path}</li>
        ))}
      </ul>
    </div>
  );
};

// Test suite using the MockOpenAPIProvider
describe('API Component with MockOpenAPIContext', () => {
  it('renders loading state when spec is null', () => {
    render(<ApiEndpointList spec={null} />);
    
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByText('Loading API specification...')).toBeInTheDocument();
  });
  
  it('renders list of API endpoints from mock spec', () => {
    render(<ApiEndpointList spec={mockOpenAPISpec} />);
    
    expect(screen.getByTestId('endpoint-list')).toBeInTheDocument();
    expect(screen.getByText('API Endpoints')).toBeInTheDocument();
    
    // Check that our mock endpoint is listed
    const endpoints = screen.getAllByTestId('endpoint');
    expect(endpoints).toHaveLength(1);
    expect(endpoints[0]).toHaveTextContent('/api/items');
  });
  
  it('works with custom spec data', () => {
    const customSpec = {
      openapi: '3.0.0',
      info: {
        title: 'Custom API',
        version: '2.0.0'
      },
      paths: {
        '/users': {},
        '/posts': {},
        '/comments': {}
      }
    };
    
    render(<ApiEndpointList spec={customSpec} />);
    
    const endpoints = screen.getAllByTestId('endpoint');
    expect(endpoints).toHaveLength(3);
    expect(endpoints[0]).toHaveTextContent('/users');
    expect(endpoints[1]).toHaveTextContent('/posts');
    expect(endpoints[2]).toHaveTextContent('/comments');
  });
});
