# MindMeld Prompt Components

This directory contains reusable React components for interacting with MindMeld prompt templates.

## Components

- **TemplateSelector**: Grid/dropdown for selecting a prompt template.
- **ParameterForm**: Dynamic form for entering template parameters.
- **PromptDisplay**: Shows the generated prompt with syntax highlighting and copy button.

## Usage Example

```tsx
import { TemplateSelector, ParameterForm, PromptDisplay } from './components/mindmeld';
import { promptApi } from '../../src/services/promptApi';

const templates = promptApi.getTemplates();

// ...state management for selectedId, paramValues, prompt, error...

<TemplateSelector templates={templates} selectedId={selectedId} onSelect={setSelectedId} />
<ParameterForm template={selectedTemplate} values={paramValues} onChange={handleParamChange} onSubmit={handleGenerate} error={error} />
<PromptDisplay prompt={prompt} />
```

## Accessibility & Responsiveness
- All components are keyboard accessible and responsive.
- Form fields use proper ARIA attributes.

## Styling
- CSS files are in `styles/` subdirectory. You may use CSS modules or styled-components as needed.

## Integration
- See `frontend/pages/PromptPage.tsx` for a full integration example.
