import { AdvancedPromptTemplate } from '../../types/promptTypes';

/**
 * Format a prompt using template and parameters without using Function constructor
 */
export function formatPromptFromTemplate(
  template: AdvancedPromptTemplate,
  params: Record<string, string>
): string {
  try {
    // Use template string approach with placeholders
    let result = template.formatFnTemplate;

    // Replace parameter values: {{paramName}}
    Object.entries(params).forEach(([key, value]) => {
      const placeholder = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
      result = result.replace(placeholder, value);
    });

    // Process conditional sections: {{#if paramName}}...{{/if}}
    const conditionalPattern = /\{\{#if\s+([^}]+)\}\}([\s\S]*?)\{\{\/if\}\}/g;
    result = result.replace(conditionalPattern, (match, condition, content) => {
      return params[condition] ? content : '';
    });

    // Process selection options: {{#select paramName value="option"}}...{{/select}}
    const selectPattern = /\{\{#select\s+([^}]+)\s+value="([^"]+)"\}\}([\s\S]*?)\{\{\/select\}\}/g;
    result = result.replace(selectPattern, (match, paramName, value, content) => {
      return params[paramName] === value ? content : '';
    });

    // Process reasoning mode blocks: {{#reasoning mode="..."}}...{{/reasoning}}
    const reasoningPattern = /\{\{#reasoning mode="([^"]+)"\}\}([\s\S]*?)\{\{\/reasoning\}\}/g;
    result = result.replace(reasoningPattern, (match, mode, content) => {
      if (template.reasoningModes && template.reasoningModes.includes(mode)) {
        return content;
      }
      return '';
    });

    // Process tone mode blocks: {{#tone mode="..."}}...{{/tone}}
    const tonePattern = /\{\{#tone mode="([^"]+)"\}\}([\s\S]*?)\{\{\/tone\}\}/g;
    result = result.replace(tonePattern, (match, mode, content) => {
      if (template.toneMode && template.toneMode === mode) {
        return content;
      }
      return '';
    });

    return result;
  } catch (error) {
    console.error('Error formatting template:', error);
    return `Error: Could not format prompt template - ${(error as Error).message}`;
  }
}

/**
 * Helper to get parameter definition from template
 */
export function getParameterDefinition(
  template: AdvancedPromptTemplate, 
  paramId: string
) {
  return template.parameters.find(p => p.id === paramId);
}

/**
 * Validate parameters against template requirements
 */
export function validateParameters(
  template: AdvancedPromptTemplate,
  params: Record<string, string>
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check required parameters
  template.parameters.forEach(param => {
    if (param.required && (!params[param.id] || params[param.id].trim() === '')) {
      errors.push(`Required parameter ${param.label} (${param.id}) is missing`);
    }
  });

  // Validate select parameters have valid values
  template.parameters
    .filter(param => param.type === 'select' && params[param.id])
    .forEach(param => {
      const value = params[param.id];
      if (param.options && !param.options.find(opt => opt.value === value)) {
        errors.push(`Parameter ${param.label} (${param.id}) has invalid value: ${value}`);
      }
    });

  return {
    valid: errors.length === 0,
    errors
  };
}
