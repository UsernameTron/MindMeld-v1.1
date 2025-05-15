import { PromptTemplate, AdvancedPromptTemplate } from '../services/PromptService';

/**
 * Converts a Markdown-based prompt template to a JSON PromptTemplate object.
 * This is a stub and should be extended to handle all advanced fields.
 */
export function markdownToPromptTemplate(markdown: string): PromptTemplate | AdvancedPromptTemplate {
  // TODO: Implement a robust Markdown parser for templates
  // For now, return a dummy template for demonstration
  return {
    id: 'from-markdown',
    name: 'Imported Template',
    description: 'Imported from Markdown',
    icon: 'import',
    color: '#000000',
    parameters: [],
    format: () => markdown
  };
}

/**
 * Converts a PromptTemplate object to a Markdown representation.
 */
export function promptTemplateToMarkdown(template: PromptTemplate | AdvancedPromptTemplate): string {
  // TODO: Implement a robust JSON-to-Markdown converter
  return `# ${template.name}\n\n${template.description}`;
}
