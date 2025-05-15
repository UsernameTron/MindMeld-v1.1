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

// Use the codeService for code analysis
const analyzeCode = async (code: string, language: string) => {
  try {
    // Get formatted analysis feedback ready for UI components
    const feedback = await codeService.getCodeFeedback(code, language);
    // Or get raw analysis results with all details
    const rawResults = await codeService.analyzeCode(code, language);
    return { feedback, rawResults };
  } catch (error) {
    console.error('Code analysis failed:', error);
    // Error handling
  }
};
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

## Code Analyzer Development Guide

The Code Analyzer feature provides real-time code analysis with detailed feedback. Here's how to extend and use it in your development:

### Component Architecture

The Code Analyzer follows the atomic design pattern with these main components:

1. **CodeAnalyzer (Organism)**: Main container component that orchestrates the analysis workflow.
2. **CodeEditor (Organism)**: Monaco-based editor with syntax highlighting and keyboard shortcuts.
3. **AnalysisResult (Organism)**: Displays analysis feedback items in a user-friendly format.
4. **AnalysisFeedbackItem (Molecule)**: Individual feedback items with severity indicators and actions.

### Using the Code Analysis Service

The `codeService` provides two primary methods for code analysis:

```typescript
// Raw analysis results with all metrics and data
const rawResults = await codeService.analyzeCode(code, language);

// Formatted feedback ready for UI components
const feedback = await codeService.getCodeFeedback(code, language);
```

### Testing Code Analyzer Components

Mock the `codeService` for component testing:

```typescript
vi.mock('../../services/codeService', () => ({
  createCodeService: vi.fn().mockReturnValue({
    getCodeFeedback: vi.fn().mockResolvedValue([
      { 
        id: 'test-1', 
        message: 'Test feedback', 
        severity: 'warning',
        category: 'performance',
        line: 5
      }
    ])
  })
}));
```

### Adding New Programming Languages

To add support for a new language:

1. Add the language to the `LANGUAGES` array in `CodeAnalyzer.tsx`
2. Add a sample snippet for the language in `SAMPLE_SNIPPETS`
3. Ensure the backend API supports the new language

### Sample Code Snippets

Sample code snippets for all supported languages are available in the `SAMPLE_SNIPPETS` object in `CodeAnalyzer.tsx`. These provide users with starting points for each language.

---
For more, see the main `README.md` and code comments in each service module.
