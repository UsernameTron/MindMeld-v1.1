import { AdvancedPromptTemplate, PromptParameter, ReasoningMode, TemplateCategory } from '../../types/promptTypes';

/**
 * Convert a markdown template string to an AdvancedPromptTemplate object
 */
export function markdownToTemplate(markdown: string): AdvancedPromptTemplate {
  // Extract title
  const titleMatch = markdown.match(/^#\s+(.*?)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Untitled Template';

  // Extract description
  const descriptionMatch = markdown.match(/^#\s+.*?\n\n([\s\S]*?)(?=^##|\s*$)/m);
  const description = descriptionMatch ? descriptionMatch[1].trim() : '';

  // Extract metadata
  const iconMatch = markdown.match(/Icon:\s*`([^`]+)`/);
  const colorMatch = markdown.match(/Color:\s*`([^`]+)`/);
  const categoryMatch = markdown.match(/Category:\s*`([^`]+)`/);

  // Extract parameters section
  const parameters: PromptParameter[] = [];
  const paramSection = markdown.match(/^##\s+Parameters\s*([\s\S]*?)(?=^##|\s*$)/m);
  if (paramSection && paramSection[1]) {
    // Parse parameter blocks (each starting with a dash)
    const paramBlocks = paramSection[1].trim().split(/^\-\s+`([^`]+)`/m).filter(Boolean);
    for (let i = 0; i < paramBlocks.length; i += 2) {
      if (i + 1 < paramBlocks.length) {
        const paramId = paramBlocks[i].trim();
        const paramBlock = paramBlocks[i + 1].trim();
        // Extract parameter info
        const labelMatch = paramBlock.match(/^:\s*(.*?)$/m);
        const typeMatch = paramBlock.match(/Type:\s*`([^`]+)`/m);
        const defaultMatch = paramBlock.match(/Default:\s*`([^`]+)`/m);
        const placeholderMatch = paramBlock.match(/Placeholder:\s*`([^`]+)`/m);
        const requiredMatch = paramBlock.match(/Required:\s*`([^`]+)`/m);
        // Parse options
        const options = [];
        const optionsMatch = paramBlock.match(/Options:\s*([\s\S]*?)(?=\n\s*\w|$)/m);
        if (optionsMatch && optionsMatch[1]) {
          const optionLines = optionsMatch[1].trim().split('\n');
          for (const line of optionLines) {
            const optMatch = line.match(/^\s*\-\s*`([^`]+)`\s*:\s*(.*?)$/);
            if (optMatch) {
              options.push({ value: optMatch[1], label: optMatch[2].trim() });
            }
          }
        }
        parameters.push({
          id: paramId,
          label: labelMatch ? labelMatch[1].trim() : paramId,
          type: (typeMatch ? typeMatch[1] : 'text') as any,
          default: defaultMatch ? defaultMatch[1] : undefined,
          placeholder: placeholderMatch ? placeholderMatch[1] : undefined,
          required: requiredMatch ? requiredMatch[1] === 'true' : false,
          options: options.length > 0 ? options : undefined
        });
      }
    }
  }

  // Extract reasoning modes
  const reasoningModes: ReasoningMode[] = [];
  const reasoningSection = markdown.match(/^##\s+Reasoning\s+Modes\s*([\s\S]*?)(?=^##|\s*$)/m);
  if (reasoningSection && reasoningSection[1]) {
    const modeLines = reasoningSection[1].trim().split('\n');
    for (const line of modeLines) {
      const modeMatch = line.match(/^\-\s+`([^`]+)`/);
      if (modeMatch) {
        reasoningModes.push(modeMatch[1] as ReasoningMode);
      }
    }
  }

  // Extract format template
  let formatTemplate = '';
  const formatSection = markdown.match(/^##\s+Format\s+Template\s*([\s\S]*?)(?=^##|\s*$)/m);
  if (formatSection && formatSection[1]) {
    const codeBlock = formatSection[1].match(/```(?:markdown|text|)\s*([\s\S]*?)```/);
    if (codeBlock && codeBlock[1]) {
      formatTemplate = codeBlock[1].trim();
    }
  }

  return {
    id: title.toLowerCase().replace(/\s+/g, '-'),
    title,
    description,
    version: '2.0',
    icon: iconMatch ? iconMatch[1] : 'document',
    color: colorMatch ? colorMatch[1] : '#4285F4',
    category: (categoryMatch ? categoryMatch[1] : 'reasoning') as TemplateCategory,
    parameters,
    reasoningModes,
    formatFnTemplate: formatTemplate,
    examples: []
  };
}

/**
 * Convert an AdvancedPromptTemplate to a markdown string
 */
export function templateToMarkdown(template: AdvancedPromptTemplate): string {
  let markdown = `# ${template.title}\n\n${template.description}\n\n`;
  markdown += `## Metadata\n`;
  markdown += `- Icon: \`${template.icon}\`\n`;
  markdown += `- Color: \`${template.color}\`\n`;
  markdown += `- Category: \`${template.category}\`\n\n`;
  markdown += `## Parameters\n`;
  for (const param of template.parameters) {
    markdown += `- \`${param.id}\`: ${param.label}\n`;
    markdown += `  - Type: \`${param.type}\`\n`;
    if (param.required) {
      markdown += `  - Required: \`true\`\n`;
    }
    if (param.default) {
      markdown += `  - Default: \`${param.default}\`\n`;
    }
    if (param.placeholder) {
      markdown += `  - Placeholder: \`${param.placeholder}\`\n`;
    }
    if (param.options && param.options.length > 0) {
      markdown += `  - Options:\n`;
      for (const option of param.options) {
        markdown += `    - \`${option.value}\`: ${option.label}\n`;
      }
    }
    markdown += '\n';
  }
  markdown += `## Reasoning Modes\n`;
  for (const mode of template.reasoningModes) {
    markdown += `- \`${mode}\`\n`;
  }
  markdown += '\n';
  markdown += `## Format Template\n\`\`\`markdown\n${template.formatFnTemplate}\n\`\`\`\n\n`;
  if (template.examples && template.examples.length > 0) {
    markdown += `## Examples\n`;
    for (const example of template.examples) {
      markdown += `### Example Input\n\`\`\`json\n${JSON.stringify(example.input, null, 2)}\n\`\`\`\n\n`;
      markdown += `### Example Output\n\`\`\`\n${example.output}\n\`\`\`\n\n`;
    }
  }
  return markdown;
}
