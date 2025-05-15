import React from 'react';
import type { AdvancedPromptTemplate, PromptParameter } from '../../../src/types/promptTypes';
import './styles/ParameterForm.css';

export interface ParameterFormProps {
  template: AdvancedPromptTemplate;
  values: Record<string, string>;
  onChange: (id: string, value: string) => void;
  onSubmit: () => void;
  error?: string;
}

export const ParameterForm: React.FC<ParameterFormProps> = ({ template, values, onChange, onSubmit, error }) => {
  const renderField = (param: PromptParameter) => {
    switch (param.type) {
      case 'text':
        return (
          <input
            id={param.id}
            type="text"
            value={values[param.id] || ''}
            placeholder={param.placeholder}
            required={param.required}
            onChange={e => onChange(param.id, e.target.value)}
            aria-required={param.required}
            aria-label={param.label}
          />
        );
      case 'textarea':
        return (
          <textarea
            id={param.id}
            value={values[param.id] || ''}
            placeholder={param.placeholder}
            required={param.required}
            onChange={e => onChange(param.id, e.target.value)}
            aria-required={param.required}
            aria-label={param.label}
          />
        );
      case 'select':
        return (
          <select
            id={param.id}
            value={values[param.id] || param.default || ''}
            required={param.required}
            onChange={e => onChange(param.id, e.target.value)}
            aria-required={param.required}
            aria-label={param.label}
          >
            <option value="" disabled>{param.placeholder || 'Select an option'}</option>
            {param.options?.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        );
      case 'number':
        return (
          <input
            id={param.id}
            type="number"
            value={values[param.id] || param.default || ''}
            required={param.required}
            onChange={e => onChange(param.id, e.target.value)}
            aria-required={param.required}
            aria-label={param.label}
          />
        );
      case 'boolean':
        return (
          <input
            id={param.id}
            type="checkbox"
            checked={values[param.id] === 'true'}
            onChange={e => onChange(param.id, e.target.checked ? 'true' : 'false')}
            aria-checked={values[param.id] === 'true'}
            aria-label={param.label}
          />
        );
      default:
        return null;
    }
  };

  return (
    <form className="mm-parameter-form" onSubmit={e => { e.preventDefault(); onSubmit(); }}>
      {template.parameters.map(param => (
        <div className="mm-form-field" key={param.id}>
          <label htmlFor={param.id}>{param.label}{param.required && <span aria-label="required">*</span>}</label>
          {renderField(param)}
          {param.helperText && <div className="mm-helper-text">{param.helperText}</div>}
        </div>
      ))}
      {error && <div className="mm-form-error" role="alert">{error}</div>}
      <button type="submit" className="mm-generate-btn">Generate Prompt</button>
    </form>
  );
};
