import React from 'react';
import { render, screen } from '@testing-library/react';
import CodeEditor from './CodeEditor';
import { AuthProvider } from '../../../context/AuthContext';

describe('CodeEditor', () => {
  it('renders the code editor container', () => {
    render(
      <AuthProvider>
        <CodeEditor initialValue="" language="javascript" onChange={() => {}} />
      </AuthProvider>
    );
    expect(screen.getByTestId('code-editor')).toBeInTheDocument();
  });
});
