import React from 'react';
import { Meta, StoryObj } from '@storybook/react';
import CodeEditor from './CodeEditor';

const meta: Meta<typeof CodeEditor> = {
  title: 'Organisms/CodeEditor',
  component: CodeEditor,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    language: {
      control: 'select',
      options: ['javascript', 'typescript', 'html', 'css', 'python', 'json'],
    },
    category: {
      control: 'select',
      options: ['analyze', 'chat', 'rewrite', 'persona'],
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof CodeEditor>;

const sampleJavaScript = `// Example code\nfunction greeting(name) {\n  return \`Hello, \\${name}!\`;\n}\n\nconsole.log(greeting('World'));
`;

const sampleTypeScript = `// TypeScript example\ninterface User {\n  name: string;\n  age: number;\n}\n\nfunction greetUser(user: User): string {\n  return \`Hello, \\${user.name}! You are \\${user.age} years old.\`;\n}\n\nconst user: User = {\n  name: 'Alice',\n  age: 30\n};\n\nconsole.log(greetUser(user));
`;

export const JavaScript: Story = {
  args: {
    value: sampleJavaScript,
    language: 'javascript',
    height: 200,
  },
};

export const TypeScript: Story = {
  args: {
    value: sampleTypeScript,
    language: 'typescript',
    height: 300,
  },
};

export const ReadOnly: Story = {
  args: {
    value: sampleJavaScript,
    readOnly: true,
    height: 200,
  },
};

export const CategoryStyling: Story = {
  render: () => (
    <div className="space-y-4">
      <CodeEditor 
        value="// Analyze category" 
        category="analyze" 
        height={100} 
      />
      <CodeEditor 
        value="// Chat category" 
        category="chat" 
        height={100} 
      />
      <CodeEditor 
        value="// Rewrite category" 
        category="rewrite" 
        height={100} 
      />
      <CodeEditor 
        value="// Persona category" 
        category="persona" 
        height={100} 
      />
    </div>
  ),
};

export const SizeVariants: Story = {
  render: () => (
    <div className="space-y-4">
      <CodeEditor 
        value="// Small size" 
        size="small" 
        height={100} 
      />
      <CodeEditor 
        value="// Medium size" 
        size="medium" 
        height={100} 
      />
      <CodeEditor 
        value="// Large size" 
        size="large" 
        height={100} 
      />
    </div>
  ),
};
