import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { Select } from './Select';

const mockOptions = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3' },
];

describe('Select Component', () => {
  it('renders with options and default value', () => {
    render(<Select options={mockOptions} value="option1" onChange={() => {}} />);

    const selectElement = screen.getByRole('combobox');
    expect(selectElement).toBeInTheDocument();
    expect(selectElement).toHaveValue('option1');

    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(3);
    expect(options[0]).toHaveValue('option1');
    expect(options[0]).toHaveTextContent('Option 1');
  });

  it('calls onChange when value changes', () => {
    const handleChange = vi.fn();

    render(<Select options={mockOptions} value="option1" onChange={handleChange} />);

    const selectElement = screen.getByRole('combobox');
    fireEvent.change(selectElement, { target: { value: 'option2' } });

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledWith('option2');
  });

  it('renders with a label', () => {
    render(<Select options={mockOptions} value="option1" onChange={() => {}} label="Test Label" />);

    expect(screen.getByText('Test Label')).toBeInTheDocument();
    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
  });

  it('displays error message when provided', () => {
    render(
      <Select
        options={mockOptions}
        value="option1"
        onChange={() => {}}
        error="This field is required"
      />
    );

    expect(screen.getByText('This field is required')).toBeInTheDocument();
    const selectElement = screen.getByRole('combobox');
    expect(selectElement.className).toContain('border-red-300');
  });

  it('disables the select when disabled prop is true', () => {
    render(<Select options={mockOptions} value="option1" onChange={() => {}} disabled />);

    const selectElement = screen.getByRole('combobox');
    expect(selectElement).toBeDisabled();
    expect(selectElement.className).toContain('cursor-not-allowed');
  });

  it('applies custom className to select element', () => {
    render(
      <Select options={mockOptions} value="option1" onChange={() => {}} className="custom-class" />
    );

    const selectElement = screen.getByRole('combobox');
    expect(selectElement.className).toContain('custom-class');
  });
});
