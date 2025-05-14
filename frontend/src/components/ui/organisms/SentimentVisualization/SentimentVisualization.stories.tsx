import React from 'react';
import type { StoryFn, Meta } from '@storybook/react';
import SentimentVisualization from './SentimentVisualization';

export default {
  title: 'UI/Organisms/SentimentVisualization',
  component: SentimentVisualization,
} as Meta;

const Template: StoryFn<typeof SentimentVisualization> = (args) => <SentimentVisualization {...args} />;

export const Default = Template.bind({});
Default.args = {};
