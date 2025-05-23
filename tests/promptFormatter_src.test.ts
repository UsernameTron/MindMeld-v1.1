import { formatPromptFromTemplate, validateParameters } from '../utils/promptFormatter';
import { AdvancedPromptTemplate } from '../types/promptTypes';

describe('Prompt Formatter', () => {
  const sampleTemplate: AdvancedPromptTemplate = {
    id: 'test-template',
    title: 'Test Template',
    description: 'A test template',
    version: '2.0',
    icon: 'test',
    color: '#000000',
    category: 'research',
    parameters: [
      {
        id: 'param1',
        label: 'Parameter 1',
        type: 'text',
        required: true
      },
      {
        id: 'param2',
        label: 'Parameter 2',
        type: 'select',
        options: [
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' }
        ]
      }
    ],
    reasoningModes: ['chain-of-thought'],
    formatFnTemplate: 'Value 1: {{param1}}, Value 2: {{param2}}'
  };

  test('formatPromptFromTemplate replaces parameters correctly', () => {
    const result = formatPromptFromTemplate(sampleTemplate, {
      param1: 'Hello',
      param2: 'World'
    });
    expect(result).toBe('Value 1: Hello, Value 2: World');
  });

  test('formatPromptFromTemplate handles conditional sections', () => {
    const templateWithConditions: AdvancedPromptTemplate = {
      ...sampleTemplate,
      formatFnTemplate: 'Base text {{#if param1}}Conditional text{{/if}}'
    };
    // parameter exists
    expect(formatPromptFromTemplate(templateWithConditions, { param1: 'value' }))
      .toBe('Base text Conditional text');
    // parameter doesn't exist
    expect(formatPromptFromTemplate(templateWithConditions, {}))
      .toBe('Base text ');
  });

  test('formatPromptFromTemplate handles selection options', () => {
    const templateWithSelections: AdvancedPromptTemplate = {
      ...sampleTemplate,
      formatFnTemplate: 'Base text {{#select param2 value="option1"}}Option 1 selected{{/select}}{{#select param2 value="option2"}}Option 2 selected{{/select}}'
    };
    expect(formatPromptFromTemplate(templateWithSelections, { param2: 'option1' }))
      .toBe('Base text Option 1 selected');
    expect(formatPromptFromTemplate(templateWithSelections, { param2: 'option2' }))
      .toBe('Base text Option 2 selected');
  });

  test('validateParameters checks required parameters', () => {
    // All required parameters provided
    expect(validateParameters(sampleTemplate, { param1: 'value' }).valid).toBe(true);
    // Missing required parameter
    expect(validateParameters(sampleTemplate, {}).valid).toBe(false);
    expect(validateParameters(sampleTemplate, {}).errors.length).toBeGreaterThan(0);
  });
});
