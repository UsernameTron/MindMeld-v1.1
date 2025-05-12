# DOM Testing in Vitest

## Issue with Jest-DOM matchers in Vitest

There is an issue with the Jest-DOM matchers (`toBeInTheDocument()`, `toHaveClass()`, etc.) not working properly in Vitest. 

## Solution: Use native DOM assertions

Instead of using the Jest-DOM matchers, use the standard JavaScript assertions with the DOM APIs. This repository includes helper functions in `dom-testing-helpers.ts` to make this easier.

## How to Update Tests

### Before:

```tsx
import { render, screen } from '@testing-library/react';

// ...
expect(element).toBeInTheDocument();
expect(element).toHaveClass('bg-red-100');
expect(element).toHaveAttribute('data-testid', 'my-element');
```

### After:

```tsx
import { render, screen } from '@testing-library/react';
import { isInDocument, hasClass, hasAttribute } from '../test-utils/dom-testing-helpers';

// ...
expect(isInDocument(element)).toBe(true);
expect(hasClass(element, 'bg-red-100')).toBe(true);
expect(hasAttribute(element, 'data-testid', 'my-element')).toBe(true);
```

Or use the native DOM APIs directly:

```tsx
expect(element).toBeTruthy();
expect(element.classList.contains('bg-red-100')).toBe(true);
expect(element.getAttribute('data-testid')).toBe('my-element');
```

## Common Replacements

| Jest-DOM Matcher | Native DOM Replacement |
| ---------------- | ---------------------- |
| `toBeInTheDocument()` | `element.isConnected` or `document.contains(element)` |
| `toHaveClass('foo')` | `element.classList.contains('foo')` |
| `toHaveAttribute('attr', 'value')` | `element.getAttribute('attr') === 'value'` |
| `toBeVisible()` | `getComputedStyle(element).display !== 'none'` |
| `toContainHTML('<div>')` | `element.innerHTML.includes('<div>')` |
| `toHaveTextContent('text')` | `element.textContent.includes('text')` |

## Notes

This is a temporary solution until the Jest-DOM matchers are properly working with Vitest.