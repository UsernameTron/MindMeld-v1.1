import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import CodeAnalyzer from '../../../../../src/components/organisms/CodeAnalyzer/CodeAnalyzer';

expect.extend(toHaveNoViolations);

describe('Accessibility: CodeAnalyzer', () => {
  test('should have no accessibility violations (WCAG 2.1 AA)', async () => {
    const { container } = render(<CodeAnalyzer />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
