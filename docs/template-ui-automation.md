# MindMeld Template System: UI Automation & Documentation

## Automated UI Test Suite

All UI and end-to-end tests for MindMeld templates are implemented using Playwright and reside in `e2e/playwright/tests/ui/` and `e2e/playwright/tests/performance/`.

### Visual Regression & Responsive Tests
- Each template (Deep Research, Advanced Reasoning, Counterfactual, Satirical Voice, Pentagram Visual) is tested for:
  - Template selection screen
  - Parameter form rendering
  - Prompt display screen
- Screenshots are captured for desktop, tablet, and mobile viewports.
- Visual tests are separate from integration tests for maintainability.

### End-to-End Workflow Tests
- Full workflow: template selection → parameter input → prompt generation.
- All templates are covered.
- Tests assert correct rendering and output for each step.

### Performance Testing
- Simultaneous template registration is tested for latency and UI responsiveness.
- Results are logged and checked against a 3s threshold.

### Running the Tests
```sh
npx playwright test e2e/playwright/tests/ui/
npx playwright test e2e/playwright/tests/performance/
```

## Template-Specific Behaviors & Type Definitions

### Template Parameters & Quirks
- Each template defines its own required/optional parameters, reasoning modes, and output constraints.
- See `src/templates/*.ts` for type-safe parameter definitions and examples.
- Example (Deep Research):
  - Required: topic, depth
  - Optional: sources, citationStyle
  - Reasoning: retrieval-augmented, chain-of-thought, etc.
  - Output: Markdown, with citations if selected

### Usage Example
```ts
import { PromptService } from './services/PromptService';
import { deepResearchTemplate } from './templates/deepResearchTemplate';

const service = new PromptService([deepResearchTemplate]);
const prompt = service.formatPrompt('deep-research', { topic: 'AI Ethics', depth: 'academic' });
console.log(prompt);
```

### Expanded Type Definitions
- All template types extend `AdvancedPromptTemplate` (see `types/promptTypes.ts`).
- Parameters, reasoning modes, and output verification are type-checked.

## Developer Notes
- All tests are fully automated and run in CI (see `.github/workflows/ci.yml`).
- For new templates, add a new entry in `src/templates/` and update the test suite.
- For quirks or special behaviors, document in this file and add test coverage.

---

_Last updated: May 15, 2025_
