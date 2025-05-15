import type { Meta, StoryObj } from '@storybook/react';
import { ErrorDisplay, ErrorDisplayProps } from './ErrorDisplay';
import React from 'react';

const meta: Meta<ErrorDisplayProps> = {
  title: 'Components/ErrorDisplay',
  component: ErrorDisplay,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<ErrorDisplayProps>;

export const Error: Story = {
  args: {
    message: 'Something went wrong.',
    title: 'Error',
    severity: 'error',
    code: 'ERR_500',
    onRetry: () => alert('Retry!'),
  },
};

export const Warning: Story = {
  args: {
    message: 'This is a warning.',
    title: 'Warning',
    severity: 'warning',
    dismissible: true,
    onDismiss: () => alert('Dismissed!'),
  },
};

export const Info: Story = {
  args: {
    message: 'This is an informational message.',
    title: 'Info',
    severity: 'info',
  },
};
