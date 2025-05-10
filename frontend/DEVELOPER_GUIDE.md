# MindMeld Frontend Developer Guide

## Dependency Injection (DI) Pattern for Services

All frontend service modules now use a factory function pattern for dependency injection. Instead of importing a singleton service, you should create an instance with the desired API client:

```ts
import { createAuthService } from './services/authService';
import { apiClient } from './services/apiClient';

const authService = createAuthService(apiClient);
```

This pattern is also used for `dataService` and `codeService`:

```ts
import { createDataService } from './services/dataService';
const dataService = createDataService(apiClient);

import { createCodeService } from './services/codeService';
const codeService = createCodeService(apiClient);
```

### Why?
- **Testability:** You can inject a mock API client in tests for full control and isolation.
- **Reliability:** No more global state or singleton leaks between tests.
- **Flexibility:** Easily swap API clients for different environments or scenarios.

## Testing Pattern
- Always inject a mock API client when testing services.
- Use Playwright for E2E security and session flows (see `e2e/playwright/`).
- Use Vitest for unit tests with full DI and mock support.

## E2E Security Flows
- See `e2e/playwright/security-flows.spec.ts` for logout, session timeout, multi-tab, and error scenario coverage.

---
For more, see the main `README.md` and code comments in each service module.
