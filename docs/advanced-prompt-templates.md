# MindMeld Advanced Prompt Template System

## Overview
This system supports both simple and advanced prompt templates for research, reasoning, counterfactual analysis, and visual generation. Templates are defined in TypeScript and can be imported/exported as Markdown or JSON.

## Template Types
- **Deep Research**: Structured research with citations.
- **Advanced Reasoning**: Stepwise, multi-mode reasoning.
- **Counterfactual Analysis**: Explore alternative scenarios.
- **Visual Prompt Generator**: Create prompts for image generation.

## Key Features
- Parameterized templates with type-safe fields
- Support for advanced reasoning modes (Chain-of-Thought, Tree-of-Thought, etc.)
- Markdown ↔ JSON migration utilities
- Backward compatibility with simple templates
- Thoroughly unit tested

## Creating a Template
1. Define parameters and format function in `src/config/promptTemplates.ts`.
2. (Optional) Add reasoning modes and output formats for advanced templates.
3. Use the `PromptService` to load, validate, and format prompts.

## Migration Utilities
- Use `markdownToPromptTemplate` and `promptTemplateToMarkdown` in `src/services/templateMigration.ts` to convert between formats.

## Example Usage
```ts
import { PromptService } from './services/PromptService';
import { promptTemplates } from './config/promptTemplates';

const service = new PromptService(promptTemplates);
const prompt = service.formatPrompt('deep-research', { topic: 'AI Ethics', depth: 'academic' });
console.log(prompt);
```

## Testing
Run `vitest` or your preferred test runner to ensure ≥85% coverage.

## Extending
- Add new reasoning modes to the `ReasoningMode` type.
- Add new templates to `promptTemplates`.
- Extend migration utilities for richer Markdown/JSON support.
