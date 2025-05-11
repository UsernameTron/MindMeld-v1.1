import type { Meta, StoryObj } from '@storybook/react';
import CodeAnalyzer from './CodeAnalyzer';

const meta: Meta<typeof CodeAnalyzer> = {
  title: 'Components/CodeAnalyzer',
  component: CodeAnalyzer,
  parameters: {
    layout: 'fullscreen',
  },
};
export default meta;
type Story = StoryObj<typeof CodeAnalyzer>;

export const Default: Story = {
  args: {
    initialCode: '// Write your code here\nlet x = 1;',
    initialLanguage: 'javascript',
    initialLayout: 'side',
  },
};

export const TypeScript: Story = {
  args: {
    initialCode: 'let y: number = 2;',
    initialLanguage: 'typescript',
    initialLayout: 'side',
  },
};

export const Python: Story = {
  args: {
    initialCode: 'def foo():\n    pass',
    initialLanguage: 'python',
    initialLayout: 'side',
  },
};

export const WithErrors: Story = {
  args: {
    initialCode: '',
    initialLanguage: 'javascript',
    initialLayout: 'side',
  },
};
