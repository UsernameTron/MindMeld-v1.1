import React from 'react';
import CodeEditor from './CodeEditor.tsx';

export default {
  title: 'Components/CodeEditor',
  component: CodeEditor,
};

export const Default = () => (
  <CodeEditor value={`function hello() {\n  console.log('Hello, world!');\n}`} language="javascript" />
);
