import React from 'react';
import { LoadingIndicator, LoadingIndicatorProps } from './LoadingIndicator';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<LoadingIndicatorProps> = {
  title: 'Components/LoadingIndicator',
  component: LoadingIndicator,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<LoadingIndicatorProps>;

export const Spinner: Story = {
  args: { variant: 'spinner', ariaLabel: 'Loading...', size: 'md' },
};

export const Dots: Story = {
  args: { variant: 'pulse', ariaLabel: 'Loading...', size: 'md' },
};

export const Bar: Story = {
  args: { variant: 'bar', ariaLabel: 'Loading...', size: 'md' },
};
