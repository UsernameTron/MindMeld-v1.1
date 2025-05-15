import { markdownToTemplate, templateToMarkdown } from '../utils/templateConverter';
import { AdvancedPromptTemplate } from '../types/promptTypes';

describe('Template Converter', () => {
  const sampleMarkdown = `# Test Template

A test template for conversion.

## Metadata
- Icon: \`test\`
- Color: \`#FF0000\`
- Category: \`research\`

## Parameters
- \`param1\`: First Parameter
  - Type: \`text\`
  - Required: \`true\`

- \`param2\`: Second Parameter
  - Type: \`select\`
  - Options:
    - \`option1\`: First Option
    - \`option2\`: Second Option

## Reasoning Modes
- \`chain-of-thought\`
- \`self-reflection\`

## Format Template
\`\`\`markdown
This is a test template with {{param1}} and {{param2}}.
\`\`\`
`;

  test('markdownToTemplate converts markdown to template object', () => {
    const template = markdownToTemplate(sampleMarkdown);
    expect(template.id).toBe('test-template');
    expect(template.title).toBe('Test Template');
    expect(template.description).toBe('A test template for conversion.');
    expect(template.icon).toBe('test');
    expect(template.color).toBe('#FF0000');
    expect(template.category).toBe('research');
    expect(template.parameters.length).toBe(2);
    expect(template.reasoningModes).toEqual(['chain-of-thought', 'self-reflection']);
    expect(template.formatFnTemplate).toBe('This is a test template with {{param1}} and {{param2}}.');
  });

  test('templateToMarkdown converts template object to markdown', () => {
    const template: AdvancedPromptTemplate = {
      id: 'test',
      title: 'Test Template',
      description: 'A test template',
      version: '2.0',
      icon: 'test',
      color: '#FF0000',
      category: 'research',
      parameters: [
        {
          id: 'param1',
          label: 'Parameter 1',
          type: 'text',
          required: true
        }
      ],
      reasoningModes: ['chain-of-thought'],
      formatFnTemplate: 'Template content {{param1}}'
    };
    const markdown = templateToMarkdown(template);
    expect(markdown).toContain('# Test Template');
    expect(markdown).toContain('A test template');
    expect(markdown).toContain('Icon: `test`');
    expect(markdown).toContain('Parameter 1');
    expect(markdown).toContain('Required: `true`');
    expect(markdown).toContain('`chain-of-thought`');
    expect(markdown).toContain('Template content {{param1}}');
  });

  test('round-trip conversion maintains template integrity', () => {
    const originalTemplate = markdownToTemplate(sampleMarkdown);
    const regeneratedMarkdown = templateToMarkdown(originalTemplate);
    const regeneratedTemplate = markdownToTemplate(regeneratedMarkdown);
    // Compare key properties to ensure they remain the same
    expect(regeneratedTemplate.id).toBe(originalTemplate.id);
    expect(regeneratedTemplate.title).toBe(originalTemplate.title);
    expect(regeneratedTemplate.parameters.length).toBe(originalTemplate.parameters.length);
    expect(regeneratedTemplate.reasoningModes).toEqual(originalTemplate.reasoningModes);
    expect(regeneratedTemplate.formatFnTemplate).toBe(originalTemplate.formatFnTemplate);
  });
});
