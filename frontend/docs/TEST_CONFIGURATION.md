# MindMeld Test Configuration Guide

This document explains the test configuration and patterns used in the MindMeld application.

## Table of Contents

1. [Overview](#overview)
2. [Path Aliasing](#path-aliasing)
3. [Mocking Strategy](#mocking-strategy)
4. [Test Utilities](#test-utilities)
5. [Best Practices](#best-practices)

## Overview

The MindMeld application uses Vitest as the testing framework with a carefully structured configuration to ensure reliable and maintainable tests. Key aspects of our test setup include:

- Centralized configuration in `vitest.config.js`
- Consistent path aliasing that matches the application structure
- Standardized mocking approach for external dependencies
- Shared test utilities for common testing patterns
- Atomic design pattern alignment in test organization

## Path Aliasing

Path aliasing is crucial for keeping imports consistent between application code and tests. Our configuration in `vitest.config.js` provides several types of aliases:

### Base Path Aliases

These aliases provide shortcuts to common directories:

```javascript
'@': path.resolve(dirname, './frontend/src'),
'@components': path.resolve(dirname, './frontend/src/components'),
'@services': path.resolve(dirname, './frontend/src/services'),
'@utils': path.resolve(dirname, './frontend/src/utils'),
'@context': path.resolve(dirname, './frontend/src/context'),
'@shims': path.resolve(dirname, './frontend/src/shims'),
'@test-utils': path.resolve(dirname, './frontend/test-utils')
```

### Relative Path Mappings

These aliases handle common relative import patterns that might cause issues:

```javascript
'./ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
'../ErrorDisplay': path.resolve(dirname, './frontend/src/components/ui/molecules/ErrorDisplay'),
'./LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
'../LoadingIndicator': path.resolve(dirname, './frontend/src/components/ui/molecules/LoadingIndicator'),
'../../utils/cn': path.resolve(dirname, './frontend/src/utils/cn'),
'../AnalysisResult/AnalysisResult': path.resolve(dirname, './frontend/src/components/ui/organisms/AnalysisResult/AnalysisResult'),
'../CodeEditor/CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor'),
'./CodeEditor': path.resolve(dirname, './frontend/src/components/ui/organisms/CodeEditor/CodeEditor')
```

### Service Mock Paths

These aliases ensure that service imports resolve to their mock versions in tests:

```javascript
'@/services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
'@/services/codeService': path.resolve(dirname, './frontend/src/__mocks__/services/codeService.js'),
'@/services/api/apiClient': path.resolve(dirname, './frontend/src/__mocks__/services/api/apiClient.js'),
'../services/authService': path.resolve(dirname, './frontend/src/__mocks__/services/authService.js'),
// ... additional service mock paths
```

## Mocking Strategy

MindMeld tests use a consistent mocking strategy:

1. **Service Mocks**: Service implementations are mocked in `__mocks__` directories
2. **Component Mocks**: External components are mocked directly in test files
3. **Browser API Mocks**: Browser APIs are mocked in `vitest.setup.ts`
4. **Next.js Mocks**: Next.js components and functions are mocked in dedicated mock files

### Mock Examples

#### Service Mock (`authService.js`)

The auth service mock implements a stateful mock that tracks authentication state:

```javascript
// Mock token storage
let storedToken = null;
let storedUser = null;

export const authService = {
  login: vi.fn().mockImplementation(async (username, password) => {
    // Implementation that updates storedToken and storedUser
  }),
  logout: vi.fn().mockImplementation(() => {
    // Implementation that clears storedToken and storedUser
  }),
  // ...other methods
};
```

#### External Component Mock (Monaco Editor)

Monaco Editor is mocked using a simplified implementation:

```javascript
vi.mock('@monaco-editor/react', () => ({
  default: MockMonacoEditor,
  useMonaco: () => MockMonaco
}));
```

## Test Utilities

We've created several test utilities to simplify common testing patterns:

### Authentication Utilities

Located in `/frontend/test-utils/AuthWrapper.tsx`, these utilities provide:

- `createAuthWrapper`: Creates a wrapper with customizable auth state
- `renderWithAuth`: Renders a component with auth context
- `mockSuccessfulLogin`: Simulates a successful login
- `mockLogout`: Simulates a logout

### Monaco Editor Utilities

Located in `/frontend/test-utils/monaco/`, these utilities provide:

- `MockMonacoEditor`: A test-friendly mock of Monaco Editor
- `mockMonaco`: Helper to set up Monaco mocks
- `resetMonacoMocks`: Helper to reset Monaco mocks between tests

### Router Utilities

Located in `/frontend/test-utils/router/`, these utilities provide:

- `RouterWrapper`: A wrapper for Next.js router
- `routerFunctions`: Mock router functions for assertions
- `resetRouterMocks`: Helper to reset router mocks

## Best Practices

When writing tests in the MindMeld application, follow these best practices:

### Import Patterns

1. **Use alias paths for imports**:
   ```tsx
   import { Button } from '@components/atoms/Button';
   ```
   instead of
   ```tsx
   import { Button } from '../../components/atoms/Button';
   ```

2. **Import mocks directly from their source**:
   ```tsx
   import { authService } from '@/__mocks__/services/authService';
   ```

3. **Use test utilities for common patterns**:
   ```tsx
   import { renderWithAuth } from '@test-utils/AuthWrapper';
   ```

### Component Testing

1. **Test component behavior, not implementation**
2. **Use data-testid attributes for selections**
3. **Test with different prop combinations**
4. **Test error and loading states**
5. **Use the atomic design pattern to organize tests**

### Mock Usage

1. **Reset mocks between tests**:
   ```tsx
   beforeEach(() => {
     vi.clearAllMocks();
     resetMonacoMocks();
   });
   ```

2. **Mock only what's necessary**
3. **Use vi.fn() for simple mocks and mockImplementation() for complex behavior**
4. **Avoid excessive mocking that makes tests brittle**

### Test Organization

1. **Group related tests in describe blocks**
2. **Use clear test names that describe the behavior being tested**
3. **Follow the atomic design pattern in test organization**
4. **Keep test files close to the components they test**

By following these patterns and practices, we can maintain a high-quality, reliable test suite for the MindMeld application.