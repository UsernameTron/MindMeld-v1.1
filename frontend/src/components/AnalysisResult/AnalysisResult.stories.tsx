import type { Meta, StoryObj } from '@storybook/react';
import AnalysisResult from './AnalysisResult.tsx';

const mockFeedback = [
  {
    id: '1',
    message: 'Unused variable',
    severity: 'warning' as const,
    category: 'style' as const,
    line: 3,
    suggestion: 'Remove the variable',
    details: 'The variable x is declared but never used.',
  },
  {
    id: '2',
    message: 'Possible null reference',
    severity: 'error' as const,
    category: 'bug' as const,
    line: 10,
    suggestion: 'Add null check',
    details: 'The value may be null at this point.',
  },
  {
    id: '3',
    message: 'Consider using const',
    severity: 'info' as const,
    category: 'best-practice' as const,
    line: 1,
  },
];

const meta: Meta<typeof AnalysisResult> = {
  title: 'Components/AnalysisResult',
  component: AnalysisResult,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof AnalysisResult>;

export const Loading: Story = {
  args: {
    feedback: [],
    loading: true,
  },
};

export const Empty: Story = {
  args: {
    feedback: [],
  },
};

export const WithFeedback: Story = {
  args: {
    feedback: mockFeedback,
  },
};

export const SingleError: Story = {
  args: {
    feedback: [mockFeedback[1]],
  },
};

export const ChatFeatureStyle: Story = {
  args: {
    feedback: mockFeedback,
    featureCategory: 'chat',
  },
};
