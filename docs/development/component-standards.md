# Component Standards: MindMeld Frontend

## Purpose
This document defines standards for building, maintaining, and documenting reusable UI components in the MindMeld frontend codebase. All components must adhere to these guidelines to ensure consistency, accessibility, and maintainability.

---

## 1. General Guidelines
- **Single Source of Truth:** Each component should have a single, consolidated implementation. Avoid duplicates.
- **Naming:** Use PascalCase for component names and file names (e.g., `Select.tsx`).
- **Location:** Place components in `frontend/src/components/ComponentName/`.
- **Props:** Clearly define all props in a TypeScript interface. Document required and optional props.
- **Variants & Extensibility:** Support visual variants and extensibility via props (e.g., `variant`, `size`, `renderOption`).

---

## 2. Accessibility (a11y)
- Use semantic HTML elements and ARIA attributes as needed.
- Ensure keyboard navigation and screen reader support.
- Use `aria-label`, `aria-invalid`, `aria-errormessage`, and other ARIA props for form controls.
- All interactive elements must be focusable and operable via keyboard.

---

## 3. Design System Compliance
- Use design system tokens for colors, spacing, and typography.
- Support all required visual variants (e.g., `primary`, `secondary`, `danger`).
- Support all required sizes (`sm`, `md`, `lg`).
- Support error and loading states.

---

## 4. Testing
- Each component must have a comprehensive test file (e.g., `Select.test.tsx`).
- Test all features, props, and edge cases (including accessibility and error states).
- Use queries that match the rendered DOM structure (e.g., Headless UI Listbox).
- All tests must pass before merging.

---

## 5. Storybook
- Each component must have a Storybook file (e.g., `Select.stories.tsx`).
- Stories must cover all variants, sizes, states, and custom rendering options.
- Use Storybook for visual regression and accessibility checks.

---

## 6. Documentation
- Document all props and usage examples in the component file and Storybook.
- Update this standards document when introducing new patterns or requirements.

---

## 7. Example: Select Component
- **File:** `frontend/src/components/Select/Select.tsx`
- **Props:** See `SelectProps` interface for all supported options.
- **Features:**
  - Single and multi-select
  - Grouped options
  - Searchable
  - Custom option rendering
  - Category and variant styling
  - Accessibility and ARIA compliance
  - Error and loading states
- **Testing:** See `Select.test.tsx` for comprehensive coverage.
- **Storybook:** See `Select.stories.tsx` for visual and interaction examples.

---

## 8. Maintenance
- Remove obsolete or duplicate component files after consolidation (keep backups as needed).
- Refactor and update imports when consolidating components.
- Ensure all usages are updated to the new implementation.

---

_Last updated: May 2025_
