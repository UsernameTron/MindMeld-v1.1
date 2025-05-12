import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import CodeEditor from './CodeEditor';

const meta: Meta<typeof CodeEditor> = {
  title: 'Components/CodeEditor',
  component: CodeEditor,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Monaco-based code editor with language detection, debouncing, and theme support.'
      }
    }
  },
  argTypes: {
    language: {
      control: 'select',
      options: ['javascript', 'typescript', 'python', 'java', 'csharp'],
      description: 'Programming language for syntax highlighting'
    },
    theme: {
      control: 'select',
      options: ['vs-dark', 'light'],
      description: 'Editor color theme'
    },
    readOnly: {
      control: 'boolean',
      description: 'Whether the editor is read-only'
    }
  }
};

export default meta;
type Story = StoryObj<typeof CodeEditor>;

export const Default: Story = {
  args: {
    initialValue: '// Type your code here\nconsole.log("Hello world!");',
    language: 'javascript',
    height: '300px',
  }
};

export const WithLanguageDetection = {
  render: () => {
    const [code, setCode] = useState('// Change this to Python\n# def hello():\n#     print("Hello world!")');
    return (
      <div>
        <p style={{ marginBottom: '10px' }}>Try uncommenting the Python code to see language switch automatically</p>
        <CodeEditor 
          initialValue={code} 
          onChange={(value: string | undefined) => setCode(value || '')} 
          height="300px"
        />
      </div>
    );
  }
};

export const DebouncedChanges = {
  render: () => {
    const [code, setCode] = useState('// Start typing to see debounced changes');
    const [changeCount, setChangeCount] = useState(0);
    
    return (
      <div>
        <p style={{ marginBottom: '10px' }}>Changes detected: {changeCount}</p>
        <CodeEditor 
          initialValue={code} 
          onChange={(value: string | undefined) => {
            setCode(value || '');
            setChangeCount(prev => prev + 1);
          }} 
          height="300px"
        />
      </div>
    );
  }
};
