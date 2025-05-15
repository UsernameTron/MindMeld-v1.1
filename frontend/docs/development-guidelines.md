# Development Guidelines

## Routing Architecture
- The project now uses the **Pages Router** exclusively (`pages/` directory).
- All App Router (`app/`) patterns and files have been removed.
- Use file-based routing in `pages/` for all new features.

## Error Handling
- Wrap all top-level pages in an `ErrorBoundary` for robust error handling.
- Use custom error pages (`pages/_error.tsx`, `pages/404.tsx`) for user-friendly error states.

## 'use client' Usage
- Avoid `'use client'` unless absolutely necessary (e.g., isolated client-only components).
- Prefer server-side rendering and static generation for all pages and most components.

## Security
- Next.js upgraded to 15.3.2 for critical SSRF fix.
- All dependencies must pass `npm audit` with no high/critical vulnerabilities.

## Testing
- Use Playwright for E2E tests and Vitest for unit/component tests.
- See `README.md` for test running instructions.
