# Navigation Shims Documentation

## Overview

This project uses a standardized approach to handling navigation in Next.js components, especially for testing. We use a "shims" layer to provide consistent navigation functionality across different environments (development, production, and testing).

## Core Files

- `/src/shims/navigation.ts`: Main shim that provides navigation functionality
- `/src/__mocks__/shims/navigation.ts`: Mock implementation for testing
- `/src/__tests__/test-utils/RouterWrapper.tsx`: Test utilities for router functions

## Usage

Instead of importing directly from Next.js, always import from our shim:

```typescript
// ❌ Don't do this:
import { useRouter } from 'next/navigation';

// ✅ Do this instead:
import { useRouter } from '@/shims/navigation';
```

## Testing

The navigation shims automatically detect the test environment and use mock implementations. The mock router functions are available for assertions:

```typescript
// In your test file:
import { routerFunctions } from '../../__tests__/test-utils/RouterWrapper';

test('my test', async () => {
  // ... test code ...
  
  // Assert navigation occurred
  expect(routerFunctions.replace).toHaveBeenCalledWith('/dashboard');
  
  // Reset mocks between tests if needed
  routerFunctions.resetMocks();
});
```

## Benefits

1. **Consistent API**: Provides a stable interface regardless of Next.js version changes
2. **Testing**: Easy mocking of navigation functions
3. **Environment Awareness**: Different behavior based on environment (dev, prod, test)
4. **Central Control**: Single place to modify navigation behavior

## Future Improvements

- Add more navigation utilities as needed
- Consider extending with custom navigation helpers for common patterns
