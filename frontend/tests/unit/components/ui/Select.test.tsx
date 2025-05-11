import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Select, SelectOption } from '../../../../src/components/ui/Select';

describe('Select Component', () => {
  const options: SelectOption[] = [
    { value: '1', label: 'One', category: 'analyze' },
    { value: '2', label: 'Two', category: 'chat' },
    { value: '3', label: 'Three', category: 'rewrite', disabled: true },
  ];

  it('renders with options and value', () => {
    render(<Select options={options} value="1" onChange={() => {}} label="Test Label" />);
    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveValue('1');
    expect(screen.getAllByRole('option')).toHaveLength(3);
  });

  it('calls onChange when value changes', () => {
    const handleChange = vi.fn();
    render(<Select options={options} value="1" onChange={handleChange} />);
    fireEvent.change(screen.getByRole('combobox'), { target: { value: '2' } });
    expect(handleChange).toHaveBeenCalledWith('2');
  });

  it('shows error message and aria attributes', () => {
    render(
      <Select options={options} value="1" onChange={() => {}} error="Required field" label="Error Test" />
    );
    expect(screen.getByText('Required field')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveAttribute('aria-invalid', 'true');
  });

  it('disables the select when disabled', () => {
    render(<Select options={options} value="1" onChange={() => {}} disabled />);
    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('applies custom className', () => {
    render(<Select options={options} value="1" onChange={() => {}} className="custom-class" />);
    expect(screen.getByRole('combobox').className).toContain('custom-class');
  });

  it('renders disabled option', () => {
    render(<Select options={options} value="1" onChange={() => {}} />);
    const option = screen.getByRole('option', { name: 'Three' });
    expect(option).toBeDisabled();
    expect(option).toHaveAttribute('aria-disabled', 'true');
  });
});
