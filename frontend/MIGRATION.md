# Next.js App Router to Pages Router Migration

## Current Architecture

This project is built using Next.js with the Pages Router architecture. The decision to use Pages Router instead of App Router was made to ensure maximum stability and compatibility with existing project patterns.

### Key Components

- **Pages Directory**: All application routes are defined in the `/pages` directory following Next.js Pages Router patterns
- **Error Handling**: Uses class-based ErrorBoundary components for graceful error handling
- **Authentication**: Implemented using `RequireAuth` component and `withAuthSSR` HOC pattern
- **Layouts**: DashboardLayout component for consistent UI across authenticated pages

## Path Aliases

The project uses the following path aliases in `tsconfig.json`:

```json
"paths": {
  "@/*": ["./src/*"],
  "@components/*": ["./src/components/*"],
  "@services/*": ["./src/services/*"],
  "@utils/*": ["./src/utils/*"],
  "@context/*": ["./src/context/*"],
  "@shims/*": ["./src/shims/*"]
}
```

## Future App Router Migration Plan

### Prerequisites

1. Wait for Next.js App Router to reach full stability and maturity (post-Q2 2025)
2. Ensure all third-party dependencies are fully compatible with App Router

### Migration Sequence

1. **Setup and Testing Environment**
   - Create parallel App Router structure without removing Pages Router
   - Update `next.config.mjs` to enable both routers simultaneously during migration

2. **Component Migration**
   - Convert class-based ErrorBoundary to use `error.js` pattern
   - Update layout components to use App Router nested layouts
   - Remove 'use client' directives where unnecessary

3. **Route Migration**
   - Start with simpler routes and migrate incrementally
   - Test each migrated route thoroughly before proceeding

4. **Authentication Refactoring**
   - Migrate authentication from HOC pattern to middleware approach
   - Update server-side authentication checks to use App Router patterns

5. **Final Testing**
   - Ensure all routes work with both routers enabled
   - Complete cross-browser and integration testing

6. **Cleanup**
   - Remove Pages Router files and patterns
   - Update documentation and developer guides

### Breaking Features to Defer

The following features should be deferred until after the migration is complete:

1. React Server Components - requires significant refactoring of data fetching patterns
2. Parallel Routes - complex UI pattern that requires careful planning
3. Route Interception - can lead to unexpected behaviors if implemented incorrectly

## Migration Testing Strategy

1. Create a comprehensive test suite that covers all user journeys
2. Test both routers in parallel to ensure parity of functionality
3. Use feature flags to gradually expose App Router routes to users
4. Monitor performance metrics and error rates during transition