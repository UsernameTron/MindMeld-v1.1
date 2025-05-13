import React from 'react';
import { ErrorDisplay, ErrorDisplayProps } from './ErrorDisplay';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<ErrorDisplayProps> = {
  title: 'Components/ErrorDisplay',
  component: ErrorDisplay,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<ErrorDisplayProps>;

export const Info: Story = {
  args: {
    title: 'Information',
    message: 'This is an informational message.',
    severity: 'info',
  },
};

export const Warning: Story = {
  args: {
    title: 'Warning',
    message: 'This is a warning message.',
    severity: 'warning',
    dismissible: true,
  },
};

export const Error: Story = {
  args: {
    title: 'Error',
    message: 'Something went wrong.',
    severity: 'error',
    code: 'ERR_500',
    onRetry: () => alert('Retry!'),
  },
};

export const Critical: Story = {
  args: {
    title: 'Critical Error',
    message: 'A critical error occurred.',
    severity: 'critical',
    showStack: true,
    stack: 'Error: Critical failure\n    at App (src/App.tsx:10)\n    at renderWithHooks (react-dom...)',
  },
};

export const Toast: Story = {
  args: {
    title: 'Toast Error',
    message: 'This is a toast notification.',
    severity: 'error',
    isToast: true,
    autoHideDuration: 3000,
  },
};
