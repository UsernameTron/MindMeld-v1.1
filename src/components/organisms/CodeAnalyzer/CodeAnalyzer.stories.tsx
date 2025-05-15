import type { Meta, StoryObj } from '@storybook/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CodeAnalyzer from './CodeAnalyzer';

const meta: Meta<typeof CodeAnalyzer> = {
  title: 'Organisms/CodeAnalyzer',
  component: CodeAnalyzer,
  decorators: [
    (Story) => (
      <QueryClientProvider client={new QueryClient()}>
        <Story />
      </QueryClientProvider>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof CodeAnalyzer>;

export const Default: Story = {
  render: () => <CodeAnalyzer />,
};

export const EmptyCode: Story = {
  render: () => <CodeAnalyzer />,
  play: async ({ canvasElement }) => {
    // Simulate empty code input
    const codeInput = canvasElement.querySelector('[aria-label="Code editor"]');
    if (codeInput) codeInput.value = '';
  },
};

export const Loading: Story = {
  render: () => <CodeAnalyzer />,
  parameters: {
    msw: [
      {
        url: '/analyze/code',
        method: 'POST',
        status: 200,
        response: () => new Promise(resolve => setTimeout(() => resolve({
          summary: { score: 90, grade: 'A', description: 'Great code!' },
          complexity: { cyclomatic: 2, linesOfCode: 10, functions: 1, maintainability: 95 },
          issues: [],
          suggestions: [],
        }), 1000)),
      },
    ],
  },
};
