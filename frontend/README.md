# MindMeld Frontend

![E2E Tests](https://github.com/YourOrg/MindMeld/actions/workflows/ci.yml/badge.svg?job=e2e-tests)

## Service Dependency Injection (DI)

All core services (auth, data, code, etc.) now use a DI factory pattern. Instead of importing a singleton, create an instance with the API client:

```ts
import { createAuthService } from './services/authService';
import { apiClient } from './services/apiClient';
const authService = createAuthService(apiClient);
```

This enables full testability and mock injection. See `DEVELOPER_GUIDE.md` for details and patterns.

<!-- Trivial change for CI/CD Phase 4 test PR -->

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Routing Architecture (Updated May 2025)
- **Pages Router** is now the exclusive routing system (`pages/` directory).
- All App Router (`app/`) patterns and files have been removed.
- For new routes, add files to `pages/`.
- See `docs/development-guidelines.md` for migration and usage details.

## Error Handling
- All top-level pages should be wrapped in an `ErrorBoundary`.
- Custom error pages: `pages/_error.tsx`, `pages/404.tsx`.

## Security Improvements
- Upgraded to Next.js 15.3.2 (fixes critical SSRF vulnerability).
- All dependencies pass `npm audit` (no high/critical vulnerabilities).
- Implemented secure authentication with HttpOnly cookies (May 2025).
- Added CORS protection via reverse proxy pattern for external APIs.

## Development Instructions (Updated)
- Use the `pages/` directory for all new features.
- Avoid `'use client'` unless required for isolated client-only components.
- See `docs/development-guidelines.md` for more.

## React/Vitest Aliasing & Select Accessibility

- **React/Vitest:** The project now enforces a single React instance for both runtime and Vitest. The `vitest.config.mts` file aliases `react` and `react-dom` to the root `node_modules` to prevent invalid hook call errors. If you see hook errors in tests, check this aliasing.
- **Select Accessibility:** The Select component now sets `aria-disabled="true"` on disabled options for improved accessibility and test reliability.

See CHANGELOG.md for more details.

## Path Alias Usage

This project uses TypeScript path aliases for cleaner and more maintainable imports. The following aliases are configured in `frontend/tsconfig.json` and supported in `frontend/vitest.config.mts`:

- `@/` → `src/`
- `@components/` → `src/components/`
- `@styles/` → `src/design/tokens/`

**Example usage:**
```ts
import { baseTokens } from '@styles/base';
import Button from '@components/ui/Button';
```

> **Note:** When adding new modules or refactoring imports, prefer using these aliases instead of long relative paths.

For test and Storybook configuration, ensure aliases are also reflected in the respective config files.

## Test File Locations and Running Tests

- All test files should be co-located with their components (e.g., `src/components/ComponentName/ComponentName.test.tsx`).
- Standard test file naming: `ComponentName.test.tsx`.
- To run all tests, from the `frontend` directory, use:
  ```sh
  npx vitest run
  ```
- To run a specific test file:
  ```sh
  npx vitest run src/components/LoadingIndicator/LoadingIndicator.test.tsx
  ```
- The test runner is configured to include all test files in the `frontend` directory.

## Navigation Shims & Testing Pattern

This project uses a navigation shim layer to standardize Next.js navigation usage and enable robust testing. Instead of importing navigation functions directly from Next.js, always use the shim:

```ts
import { useRouter } from '@/shims/navigation';
```

- The shim automatically provides the real Next.js router in production and a mock router in test environments.
- For details and usage examples, see [`docs/navigation-shims.md`](./docs/navigation-shims.md).

This ensures:
- Consistent navigation API across the codebase
- Easy mocking and assertion of navigation in tests
- Centralized control for future navigation changes

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
