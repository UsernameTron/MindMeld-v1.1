import { PromptService } from '../services/promptService';
import { AdvancedPromptTemplate } from '../types/promptTypes';
import { markdownToTemplate, templateToMarkdown } from '../utils/templateConverter';
import fs from 'fs';
import path from 'path';

// Mock filesystem for integration tests
jest.mock('fs');
jest.mock('path');

describe('Prompt Template System Integration', () => {
  let service: PromptService;
  let tempDir: string;

  beforeEach(() => {
    service = new PromptService();
    tempDir = '/tmp/test-prompts';
    // Mock filesystem
    (fs.existsSync as jest.Mock).mockImplementation(() => true);
    (fs.mkdirSync as jest.Mock).mockImplementation(() => undefined);
    (fs.readdirSync as jest.Mock).mockImplementation(() => []);
    (path.resolve as jest.Mock).mockImplementation((...args) => args.join('/'));
    (path.join as jest.Mock).mockImplementation((...args) => args.join('/'));
  });

  test('Full template lifecycle - creation, conversion, formatting', () => {
    // 1. Create a template programmatically
    const template: AdvancedPromptTemplate = {
      id: 'lifecycle-test',
      title: 'Lifecycle Test',
      description: 'Testing the full template lifecycle',
      version: '2.0',
      icon: 'test',
      color: '#4285F4',
      category: 'reasoning',
      parameters: [
        {
          id: 'input',
          label: 'Input Text',
          type: 'textarea',
          placeholder: 'Enter text to analyze',
          required: true
        },
        {
          id: 'depth',
          label: 'Analysis Depth',
          type: 'select',
          options: [
            { value: 'basic', label: 'Basic' },
            { value: 'detailed', label: 'Detailed' },
            { value: 'comprehensive', label: 'Comprehensive' }
          ],
          default: 'detailed'
        }
      ],
      reasoningModes: ['chain-of-thought', 'self-reflection'],
      formatFnTemplate: `# Analysis Request\n\n## Input Text\n{{input}}\n\n## Analysis Parameters\n{{#select depth value="basic"}}\n- Depth: Basic analysis\n{{/select}}\n{{#select depth value="detailed"}}\n- Depth: Detailed analysis\n{{/select}}\n{{#select depth value="comprehensive"}}\n- Depth: Comprehensive analysis\n{{/select}}\n\n## Instructions\nAnalyze the provided text using chain-of-thought reasoning and self-reflection.\n`,
      outputFormat: 'markdown'
    };

    // 2. Convert to markdown
    const markdown = templateToMarkdown(template);
    expect(markdown).toContain('# Lifecycle Test');
    expect(markdown).toContain('Testing the full template lifecycle');

    // 3. Convert back to template
    const reconvertedTemplate = markdownToTemplate(markdown);
    expect(reconvertedTemplate.id).toBe('lifecycle-test');
    expect(reconvertedTemplate.parameters.length).toBe(2);

    // 4. Register with service
    // Feature flag respected in registerTemplate
    service.registerTemplate(reconvertedTemplate);
    expect(service.getTemplateById('lifecycle-test')).toBeTruthy();

    // 5. Generate prompt
    const prompt = service.generatePrompt('lifecycle-test', {
      input: 'This is a test input',
      depth: 'detailed'
    });

    // 6. Verify formatted output
    expect(prompt).toContain('# Analysis Request');
    expect(prompt).toContain('This is a test input');
    expect(prompt).toContain('Depth: Detailed analysis');
    expect(prompt).toContain('chain-of-thought reasoning and self-reflection');

    // 7. Test category filtering
    const reasoningTemplates = service.getTemplatesByCategory('reasoning');
    expect(reasoningTemplates.length).toBe(1);
    expect(reasoningTemplates[0].id).toBe('lifecycle-test');
  });
});
