import type { Meta, StoryObj } from '@storybook/react';
import { LoadingIndicator, LoadingIndicatorProps } from './LoadingIndicator';
import React from 'react';

const meta: Meta<LoadingIndicatorProps> = {
  title: 'Components/LoadingIndicator',
  component: LoadingIndicator,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<LoadingIndicatorProps>;

export const Small: Story = {
  args: { size: 'sm', ariaLabel: 'Loading small' },
};

export const Medium: Story = {
  args: { size: 'md', ariaLabel: 'Loading medium' },
};

export const Large: Story = {
  args: { size: 'lg', ariaLabel: 'Loading large' },
};

export const CustomColor: Story = {
  args: { size: 'md', color: '#34A853', ariaLabel: 'Loading green' },
};
