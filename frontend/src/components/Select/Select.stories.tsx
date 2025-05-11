import React from 'react';
import { Select, SelectProps } from './Select';
import type { Meta, StoryObj } from '@storybook/react';

const options = [
  { value: '1', label: 'Option 1', category: 'analyze' },
  { value: '2', label: 'Option 2', category: 'chat', disabled: true },
  { value: '3', label: 'Option 3', category: 'rewrite' },
  { value: '4', label: 'Option 4', category: 'persona', group: 'Group A' },
  { value: '5', label: 'Option 5', group: 'Group A' },
  { value: '6', label: 'Option 6', group: 'Group B' },
];

const meta: Meta<SelectProps> = {
  title: 'Components/Select',
  component: Select,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<SelectProps>;

export const Default: Story = {
  args: {
    options,
    placeholder: 'Select an option',
  },
};

export const Grouped: Story = {
  args: {
    options,
    placeholder: 'Select grouped',
  },
};

export const Disabled: Story = {
  args: {
    options,
    disabled: true,
    placeholder: 'Disabled select',
  },
};

export const CustomOption: Story = {
  args: {
    options: options.map(opt => ({ ...opt, icon: <span className="inline-block w-3 h-3 bg-blue-400 rounded-full mr-2" /> })),
    renderOption: (option, selected) => (
      <span className="flex items-center">
        {option.icon}
        <span>{option.label}</span>
        {selected && <span className="ml-2 text-xs text-blue-500">(selected)</span>}
      </span>
    ),
    placeholder: 'Custom option',
  },
};
