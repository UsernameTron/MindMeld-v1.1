import { isAdvancedTemplate } from '../types/promptTypes';

describe('Type Guards', () => {
  test('isAdvancedTemplate correctly identifies basic templates', () => {
    const basicTemplate = {
      id: 'basic',
      title: 'Basic Template',
      description: 'A simple template'
    };
    expect(isAdvancedTemplate(basicTemplate)).toBe(false);
  });

  test('isAdvancedTemplate correctly identifies advanced templates', () => {
    const advancedTemplate = {
      id: 'advanced',
      title: 'Advanced Template',
      description: 'An advanced template',
      version: '2.0',
      icon: 'star',
      color: '#4285F4',
      category: 'research',
      parameters: [],
      reasoningModes: ['chain-of-thought'],
      formatFnTemplate: 'Template string'
    };
    expect(isAdvancedTemplate(advancedTemplate)).toBe(true);
  });
});
