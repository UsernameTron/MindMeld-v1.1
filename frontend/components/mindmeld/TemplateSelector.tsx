import React from 'react';
import type { PromptTemplate } from '../../../src/types/promptTypes';
import './styles/TemplateSelector.css';

export interface TemplateSelectorProps {
  templates: PromptTemplate[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({ templates, selectedId, onSelect }) => (
  <div className="mm-template-selector" role="listbox" aria-label="Prompt Templates">
    {templates.map((tpl) => (
      <button
        key={tpl.id}
        className={`mm-template-card${selectedId === tpl.id ? ' selected' : ''}`}
        onClick={() => onSelect(tpl.id)}
        aria-selected={selectedId === tpl.id}
        tabIndex={0}
      >
        {'icon' in tpl && tpl.icon && <span className="mm-template-icon" aria-hidden>{tpl.icon}</span>}
        <div className="mm-template-info">
          <div className="mm-template-title">{tpl.title}</div>
          <div className="mm-template-desc">{tpl.description}</div>
        </div>
      </button>
    ))}
  </div>
);
