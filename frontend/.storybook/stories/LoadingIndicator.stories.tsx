import React from 'react';
import { LoadingIndicator, LoadingIndicatorVariant } from '@/components/ui/LoadingIndicator';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof LoadingIndicator> = {
  title: 'Components/UI/LoadingIndicator',
  component: LoadingIndicator,
  argTypes: {
    variant: {
      control: 'select',
      options: ['analyze', 'chat', 'rewrite', 'persona'],
    },
    size: {
      control: { type: 'number', min: 12, max: 64, step: 4 },
    },
    label: { control: 'text' },
  },
  parameters: {
    docs: {
      description: {
        component:
          'Accessible, animated loading spinner supporting feature category colors. Uses Tailwind for animation and design tokens for color.',
      },
    },
  },
};
export default meta;

type Story = StoryObj<typeof LoadingIndicator>;

export const Default: Story = {
  args: {},
};

export const Analyze: Story = {
  args: { variant: 'analyze', label: 'Loading (analyze)' },
};

export const Chat: Story = {
  args: { variant: 'chat', label: 'Loading (chat)' },
};

export const Rewrite: Story = {
  args: { variant: 'rewrite', label: 'Loading (rewrite)' },
};

export const Persona: Story = {
  args: { variant: 'persona', label: 'Loading (persona)' },
};

export const Large: Story = {
  args: { size: 48, label: 'Loading large', variant: 'analyze' },
};

export const InButton: Story = {
  render: (args) => (
    <button type="button" className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded">
      <LoadingIndicator {...args} size={16} label="Loading in button" />
      Loading
    </button>
  ),
  args: { variant: 'chat' },
};
