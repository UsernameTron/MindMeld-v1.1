import type { Meta, StoryObj } from '@storybook/react';
import ThemeTester from './ThemeTester';

const meta: Meta<typeof ThemeTester> = {
  title: 'Design System/Theme Tester',
  component: ThemeTester,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ThemeTester>;

export const Default: Story = {};
