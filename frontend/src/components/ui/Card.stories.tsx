import React from 'react';
import { Meta, StoryObj } from '@storybook/react';
import Card, { CardProps } from './Card';

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'outlined', 'elevated'],
    },
    header: { control: 'text' },
    footer: { control: 'text' },
    actions: { control: 'text' },
    children: { control: 'text' },
  },
};
export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    header: 'Card Header',
    children: 'This is the card content.',
    footer: 'Card Footer',
    variant: 'default',
  },
};

export const Outlined: Story = {
  args: {
    header: 'Outlined Card',
    children: 'Outlined variant with primary border.',
    footer: 'Footer',
    variant: 'outlined',
  },
};

export const Elevated: Story = {
  args: {
    header: 'Elevated Card',
    children: 'Elevated variant with shadow.',
    footer: 'Footer',
    variant: 'elevated',
  },
};

export const WithActions: Story = {
  args: {
    header: 'Card with Actions',
    children: 'You can add actions to the header.',
    actions: <button className="btn btn-primary">Action</button>,
    variant: 'default',
  },
};

export const NoHeaderFooter: Story = {
  args: {
    children: 'Card without header or footer.',
    variant: 'default',
  },
};
