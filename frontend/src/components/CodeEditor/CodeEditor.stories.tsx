import React from 'react';
import CodeEditor from './CodeEditor';

export default {
  title: 'Components/CodeEditor',
  component: CodeEditor,
};

export const Default = () => (
  <CodeEditor initialValue={`function hello() {\n  console.log('Hello, world!');\n}`} language="javascript" />
);
