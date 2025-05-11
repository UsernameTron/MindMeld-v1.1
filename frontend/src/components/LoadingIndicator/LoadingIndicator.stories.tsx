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
  args: { variant: 'spinner', label: 'Loading...', size: 'md' },
};

export const Dots: Story = {
  args: { variant: 'dots', label: 'Loading...', size: 'md' },
};

export const Bar: Story = {
  args: { variant: 'bar', label: 'Loading...', size: 'md' },
};

export const Skeleton: Story = {
  args: { variant: 'skeleton', label: 'Loading...', size: 'md' },
};

export const FullPage: Story = {
  args: { variant: 'spinner', fullPage: true, backdrop: true, label: 'Loading full page...', size: 'lg' },
};
