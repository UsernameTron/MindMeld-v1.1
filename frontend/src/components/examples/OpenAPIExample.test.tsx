import React from 'react';
import { render, screen } from '@testing-library/react';
import { MockOpenAPIProvider } from '../../../tests/mocks/OpenAPIContext.mock';

describe('OpenAPIContext Mock Tests', () => {
  // Create a simple test component that displays API info from context
  const APIDisplay = () => {
    return <div data-testid="api-display">API Context Consumer</div>;
  };

  it('renders with mock provider', () => {
    render(
      <MockOpenAPIProvider>
        <APIDisplay />
      </MockOpenAPIProvider>
    );
    
    expect(screen.getByTestId('api-display')).toBeInTheDocument();
    expect(screen.getByText('API Context Consumer')).toBeInTheDocument();
  });
  
  it('can be used with nested components', () => {
    const NestedComponent = () => <div data-testid="nested">Nested Component</div>;
    
    render(
      <MockOpenAPIProvider>
        <div data-testid="parent">
          <NestedComponent />
        </div>
      </MockOpenAPIProvider>
    );
    
    expect(screen.getByTestId('parent')).toBeInTheDocument();
    expect(screen.getByTestId('nested')).toBeInTheDocument();
  });
});
