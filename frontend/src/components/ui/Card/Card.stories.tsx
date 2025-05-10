import type { Meta, StoryObj } from '@storybook/react';
import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, type CardProps } from './Card.js';

const meta: Meta<typeof Card> = {
  title: 'Components/Card',
  component: Card,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'ghost'],
    },
    category: {
      control: 'select',
      options: ['default', 'analyze', 'chat', 'rewrite', 'persona'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    withHover: {
      control: 'boolean',
    },
    hasHeaderBorder: {
      control: 'boolean',
    },
    hasFooterBorder: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    variant: 'default',
    category: 'default',
    size: 'md',
    withHover: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card description goes here</CardDescription>
      </CardHeader>
      <CardContent>
        <p>This is the main content of the card.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-neutral-500">Card footer</p>
      </CardFooter>
    </Card>
  ),
};

export const Analyze: Story = {
  args: {
    variant: 'default',
    category: 'analyze',
    size: 'md',
    withHover: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle className="text-analyze-dark">Code Analyzer</CardTitle>
        <CardDescription>Analyze your code for issues</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Find bugs and performance issues in your code.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-analyze-default">View analyzer</p>
      </CardFooter>
    </Card>
  ),
};

export const Chat: Story = {
  args: {
    variant: 'default',
    category: 'chat',
    size: 'md',
    withHover: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle className="text-chat-dark">AI Chat</CardTitle>
        <CardDescription>Chat with our AI assistant</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Get help with your coding questions and tasks.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-chat-default">Start chatting</p>
      </CardFooter>
    </Card>
  ),
};

export const Rewrite: Story = {
  args: {
    variant: 'default',
    category: 'rewrite',
    size: 'md',
    withHover: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle className="text-rewrite-dark">Code Rewriter</CardTitle>
        <CardDescription>Transform your code</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Rewrite code to different languages or patterns.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-rewrite-default">Start rewriting</p>
      </CardFooter>
    </Card>
  ),
};

export const Persona: Story = {
  args: {
    variant: 'default',
    category: 'persona',
    size: 'md',
    withHover: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle className="text-persona-dark">Personas</CardTitle>
        <CardDescription>Access specialized assistants</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Use AI assistants with different expertise.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-persona-default">Choose persona</p>
      </CardFooter>
    </Card>
  ),
};

export const NoHover: Story = {
  args: {
    variant: 'default',
    category: 'default',
    size: 'md',
    withHover: false,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader>
        <CardTitle>No Hover Effect</CardTitle>
        <CardDescription>This card does not have a hover effect</CardDescription>
      </CardHeader>
      <CardContent>
        <p>The hover shadow effect is disabled.</p>
      </CardContent>
    </Card>
  ),
};

export const WithBorders: Story = {
  args: {
    variant: 'default',
    category: 'default',
    size: 'md',
    withHover: true,
    hasHeaderBorder: true,
    hasFooterBorder: true,
  },
  render: (args: CardProps) => (
    <Card {...args} className="w-[350px]">
      <CardHeader hasBottomBorder={args.hasHeaderBorder}>
        <CardTitle>With Borders</CardTitle>
        <CardDescription>This card has header and footer borders</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Notice the separation between sections.</p>
      </CardContent>
      <CardFooter hasTopBorder={args.hasFooterBorder}>
        <p className="text-sm text-neutral-500">Footer with border</p>
      </CardFooter>
    </Card>
  ),
};
