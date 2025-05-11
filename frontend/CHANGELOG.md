# Changelog

## [Unreleased]

### Fixed
- Ensured only a single React instance is used for both runtime and testing (Vitest) to prevent invalid hook call errors. Updated `vitest.config.mts` to alias `react` and `react-dom` to the root `node_modules`.
- Updated Select component to add `aria-disabled="true"` to disabled options for accessibility and to pass all tests.
- Improved test mocks to match Headless UI behavior for accessibility attributes.

### Notes
- **React aliasing for Vitest:** If you encounter hook call errors or React context issues in tests, ensure your `vitest.config.mts` aliases both `react` and `react-dom` to the root `node_modules` directory. This prevents multiple React instances in monorepo or nested setups.
- **Accessibility:** The Select component now always renders `aria-disabled="true"` on disabled options, improving screen reader support and testability.
