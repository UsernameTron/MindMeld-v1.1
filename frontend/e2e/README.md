# E2E Tests

Playwright E2E tests should be run using the Playwright CLI, not with Vitest. Example:

```
npx playwright test
```

If you see errors about Playwright tests being run by Vitest, ensure your test matcher in `vitest.config.*` excludes the `e2e/` and `tests/` folders, or move E2E tests outside the default test match patterns.
