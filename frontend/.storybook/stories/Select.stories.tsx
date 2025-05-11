import React, { useState } from 'react';
import { Select, SelectOption } from '../../src/components/ui/Select';

export default {
  title: 'UI/Select',
  component: Select,
};

const options: SelectOption[] = [
  { value: 'analyze', label: 'Analyze', category: 'analyze' },
  { value: 'chat', label: 'Chat', category: 'chat' },
  { value: 'rewrite', label: 'Rewrite', category: 'rewrite' },
  { value: 'persona', label: 'Persona', category: 'persona' },
  { value: 'disabled', label: 'Disabled', disabled: true },
];

export const Default = () => {
  const [value, setValue] = useState('analyze');
  return (
    <Select
      options={options}
      value={value}
      onChange={setValue}
      label="Feature Category"
      placeholder="Select a feature"
    />
  );
};

export const WithError = () => {
  const [value, setValue] = useState('');
  return (
    <Select
      options={options}
      value={value}
      onChange={setValue}
      label="With Error"
      error="This field is required"
      placeholder="Select a feature"
    />
  );
};

export const Disabled = () => (
  <Select
    options={options}
    value={''}
    onChange={() => {}}
    label="Disabled"
    disabled
  />
);

export const Variants = () => {
  const [value, setValue] = useState('chat');
  return (
    <div className="space-y-4">
      <Select
        options={options}
        value={value}
        onChange={setValue}
        label="Primary Variant"
        variant="primary"
      />
      <Select
        options={options}
        value={value}
        onChange={setValue}
        label="Secondary Variant"
        variant="secondary"
      />
      <Select
        options={options}
        value={value}
        onChange={setValue}
        label="Danger Variant"
        variant="danger"
      />
    </div>
  );
};
