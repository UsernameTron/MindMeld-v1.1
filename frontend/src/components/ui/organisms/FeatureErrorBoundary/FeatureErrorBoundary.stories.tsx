import React from 'react';
import { FeatureErrorBoundary, FeatureErrorBoundaryProps } from './FeatureErrorBoundary';
import type { Meta, StoryObj } from '@storybook/react';

const meta = {
  title: 'Components/FeatureErrorBoundary',
  component: FeatureErrorBoundary,
  tags: ['autodocs'],
};
export default meta;

type Story = StoryObj<FeatureErrorBoundaryProps>;

const Thrower: React.FC = () => {
  throw new Error('Test error!');
};

export const Default: Story = {
  render: () => (
    <FeatureErrorBoundary>
      <Thrower />
    </FeatureErrorBoundary>
  ),
};

export const CustomFallback: Story = {
  render: () => (
    <FeatureErrorBoundary
      fallback={({ error, resetErrorBoundary }) => (
        <div className="p-4 bg-yellow-50 border border-yellow-400 rounded text-yellow-800">
          <div className="font-bold mb-2">Custom Fallback</div>
          <div>{error.message}</div>
          <button onClick={resetErrorBoundary} className="mt-2 px-3 py-1 rounded bg-blue-500 text-white text-xs">Try Again</button>
        </div>
      )}
    >
      <Thrower />
    </FeatureErrorBoundary>
  ),
};

export const WithDetails: Story = {
  render: () => (
    <FeatureErrorBoundary showDetails>
      <Thrower />
    </FeatureErrorBoundary>
  ),
};
