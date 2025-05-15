# CI trigger

# MindMeld Code Analyzer

## Overview
The Code Analyzer feature provides an accessible, responsive, and user-friendly interface for analyzing code quality directly in the MindMeld frontend. It integrates the Monaco editor for code input, supports multiple languages, and displays analysis results with severity indicators and detailed feedback.

## Usage
1. Navigate to `/code-analyzer` in the application.
2. Enter or paste your code in the Monaco editor.
3. Select the programming language from the dropdown.
4. Click the "Analyze" button to run the code quality analysis.
5. View results below the editor, including severity, messages, and details.
6. Use keyboard navigation and ARIA landmarks for accessibility.

## Features
- Monaco editor with language selection and error display
- Accessible UI (WCAG 2.1 AA compliant, ARIA attributes, keyboard navigation)
- Responsive layout and theme support
- React Query for API integration and state management
- Error and loading states for all user flows
- Expand/collapse for detailed analysis results
- Storybook stories for all components
- Unit tests with ≥80% coverage

## Accessibility & Performance
- All components are tested with axe and meet WCAG 2.1 AA standards.
- Monaco editor is lazy-loaded and SSR-disabled for optimal performance.
- Keyboard navigation and screen reader support are fully implemented.

## Testing & Coverage
- Run all tests and coverage:
  ```sh
  npx vitest run --coverage
  ```
- Coverage for Code Analyzer feature is ≥80%.

## Demo
A screen recording demonstrating the full workflow, including error states and accessibility features, is available at:
[code-analyzer-demo.mp4](<ADD_LINK_HERE>)

## API
- The feature uses `/analyze/code` endpoint for code analysis.
- See `src/services/codeService.ts` for integration details.

## Contributing
- See Storybook stories for usage examples.
- All new features must maintain accessibility and test coverage standards.

---
