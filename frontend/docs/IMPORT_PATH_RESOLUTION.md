# Import Path Resolution and Monaco Testing Guide

This document explains the improvements made to path resolution in the MindMeld application, focusing on handling component import paths in tests and Monaco editor testing.

## Table of Contents

1. [Overview](#overview)
2. [Path Aliasing Improvements](#path-aliasing-improvements)
3. [Monaco Editor Testing](#monaco-editor-testing)
4. [Authentication Context in Tests](#authentication-context-in-tests)
5. [Remaining Issues](#remaining-issues)
6. [Best Practices](#best-practices)

## Overview

Testing complex React components in the MindMeld application requires accurate path resolution and proper mocking of external dependencies. This document covers the improvements made to path resolution in tests and the introduction of Monaco editor testing utilities.

## Path Aliasing Improvements

### Updated Configuration in vitest.config.js

We've enhanced the path alias configuration to ensure components can be imported consistently across the application and tests:

```javascript
alias: {
  // Base path aliases
  '@': path.resolve(dirname, './frontend/src'),
  '@components': path.resolve(dirname, './frontend/src/components'),
  '@services': path.resolve(dirname, './frontend/src/services'),
  '@utils': path.resolve(dirname, './frontend/src/utils'),
  '@context': path.resolve(dirname, './frontend/src/context'),
  '@shims': path.resolve(dirname, './frontend/src/shims'),
  '@test-utils': path.resolve(dirname, './frontend/test-utils'),
  
  // Relative path mappings for component imports
  './ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
  '../ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
  './LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
  '../LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
  '../../utils/cn': path.resolve(dirname, './frontend/src/utils/cn'),
  '../AnalysisResult/AnalysisResult': path.resolve(dirname, './frontend/src/components/ui/organisms/AnalysisResult/AnalysisResult'),
  '../CodeEditor/CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor'),
  './CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor'),
}
```

### Benefits

1. **Consistent Resolution**: Imports like `../ErrorDisplay` now resolve correctly across different directory levels
2. **Simplified Imports**: Components can be imported with shorter paths
3. **Path Flexibility**: Handles both direct and relative imports

### Implementation Notes

- Added more aliases for common components like LoadingIndicator
- Ensured CodeEditor component resolves properly for nested imports
- Added @test-utils alias for accessing testing utilities

## Monaco Editor Testing

To simplify testing components that use Monaco Editor, we've created dedicated test utilities in `/frontend/test-utils/monaco/`:

### MonacoMock.tsx

This utility provides:

1. A mock implementation of Monaco Editor
2. Supporting utilities for Monaco editor testing
3. Type-compatible API with the real Monaco editor

```javascript
// Mock the Monaco editor using our shared test utilities
vi.mock('@monaco-editor/react', () => ({
  default: MockMonacoEditor,
  useMonaco: () => MockMonaco
}));
```

### Key Features

- **Easy Setup**: Simple function to set up Monaco mocks
- **Realistic Behavior**: Mock editor that behaves like the real one
- **Event Support**: Handles change events and value updates
- **Editor Reference**: Provides a ref API similar to Monaco

### Usage Example

```javascript
import { mockMonaco } from '@test-utils/monaco';

// Set up Monaco mocks
mockMonaco();

describe('CodeEditor', () => {
  test('allows typing code', () => {
    render(<CodeEditor />);
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { target: { value: 'const x = 5;' } });
    expect(editor).toHaveValue('const x = 5;');
  });
});
```

## Authentication Context in Tests

Many components require authentication context to render properly. We've created an AuthWrapper utility to make testing these components easier:

### AuthWrapper.tsx

This utility provides:

1. A test wrapper that provides authentication context
2. Helper functions for common authentication testing patterns
3. Easy configuration of authentication state

```javascript
// Use the authentication wrapper in tests
import { renderWithAuth } from '@test-utils/AuthWrapper';

test('component renders in authenticated state', () => {
  renderWithAuth(<MyComponent />);
  // Test assertions...
});
```

### Implementation Notes

- Added mock functions for common auth operations
- Support for both authenticated and unauthenticated states
- Easy configuration for specific test scenarios

## Remaining Issues

While most path resolution issues have been addressed, some challenges remain:

1. **Legacy Components**: Some components in alternative locations may still have path issues
2. **Deep Nesting**: Very deeply nested components may require additional aliases
3. **Next.js Router**: Some components require improved Next.js router mocking

## Best Practices

When working with imports and testing in the MindMeld application:

1. **Prefer Alias Paths**: Use @components/... instead of relative paths
2. **Atomic Design Structure**: Follow the atoms/molecules/organisms structure
3. **AuthWrapper for Auth Components**: Use renderWithAuth for components that need auth
4. **Monaco Testing**: Use the Monaco test utilities for editor components
5. **Mock Services Consistently**: Import mocks from @/__mocks__/services/...

By following these practices, tests will be more reliable and less prone to import issues.