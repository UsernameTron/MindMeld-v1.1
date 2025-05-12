// test-setup.ts
import { expect } from 'vitest';
import * as domMatchers from '@testing-library/jest-dom/matchers';
import { configure } from '@testing-library/dom';

// Add all matchers from jest-dom
expect.extend(domMatchers);

// Configure testing library
configure({
  testIdAttribute: 'data-testid',
});