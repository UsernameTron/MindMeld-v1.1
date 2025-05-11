import React from 'react';
import { render, screen } from '@testing-library/react';
import CodeEditor from './CodeEditor.tsx';

describe('CodeEditor', () => {
  it('renders without crashing', () => {
    render(<CodeEditor initialValue="console.log('Hello, world!');" />);
    expect(screen.getByRole('application')).toBeInTheDocument();
  });
});
