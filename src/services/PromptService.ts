import {
  PromptTemplate,
  AdvancedPromptTemplate,
  isAdvancedTemplate,
  ReasoningMode,
  ToneMode,
  TemplateCategory,
  OutputFormat,
  TemplateConstraints,
  OutputVerification
} from '../../types/promptTypes';
import { formatPromptFromTemplate, validateParameters } from '../utils/promptFormatter';
import { Logger } from '../utils/logger';

export class PromptService {
  private templates: Map<string, PromptTemplate> = new Map();
  private logger: Logger;

  constructor(logger?: Logger) {
    this.logger = logger || new Logger('PromptService');
  }

  registerTemplate(template: PromptTemplate): void {
    if (this.templates.has(template.id)) {
      this.logger.warn(`Template with ID ${template.id} already exists and will be overwritten.`);
    }
    this.templates.set(template.id, template);
    if (isAdvancedTemplate(template)) {
      this.logger.info(`Registered advanced template: ${template.title} (${template.id}) with ${template.reasoningModes.length} reasoning modes`);
      this.validateTemplateStructure(template);
    } else {
      this.logger.info(`Registered basic template: ${template.title} (${template.id})`);
    }
  }

  getAllTemplates(): PromptTemplate[] {
    return Array.from(this.templates.values());
  }

  getTemplateById(id: string): PromptTemplate | undefined {
    return this.templates.get(id);
  }

  getTemplatesByCategory(category: TemplateCategory): AdvancedPromptTemplate[] {
    return Array.from(this.templates.values())
      .filter((template): template is AdvancedPromptTemplate =>
        isAdvancedTemplate(template) && template.category === category
      );
  }

  getTemplatesByReasoningMode(reasoningMode: ReasoningMode): AdvancedPromptTemplate[] {
    return Array.from(this.templates.values())
      .filter((template): template is AdvancedPromptTemplate =>
        isAdvancedTemplate(template) && template.reasoningModes.includes(reasoningMode)
      );
  }

  getTemplatesByToneMode(toneMode: ToneMode): AdvancedPromptTemplate[] {
    return Array.from(this.templates.values())
      .filter((template): template is AdvancedPromptTemplate =>
        isAdvancedTemplate(template) && template.toneMode === toneMode
      );
  }

  getTemplatesByOutputFormat(outputFormat: OutputFormat): AdvancedPromptTemplate[] {
    return Array.from(this.templates.values())
      .filter((template): template is AdvancedPromptTemplate =>
        isAdvancedTemplate(template) && template.outputFormat === outputFormat
      );
  }

  generatePrompt(templateId: string, parameters: Record<string, string>, options: { enforceConstraints?: boolean } = {}): string {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template with ID ${templateId} not found`);
    }
    if (!isAdvancedTemplate(template)) {
      return `${template.title}\n\n${template.description}`;
    }
    if (options.enforceConstraints !== false) {
      const validationResult = validateParameters(template, parameters);
      if (!validationResult.valid) {
        throw new Error(`Parameter validation failed: ${validationResult.errors.join(', ')}`);
      }
    }
    try {
      const processedParams = this.preprocessParameters(template, parameters);
      const prompt = formatPromptFromTemplate(template, processedParams);
      const finalPrompt = this.postprocessPrompt(template, prompt);
      this.logger.info(`Generated prompt from template: ${template.title} (${template.id})`);
      return finalPrompt;
    } catch (error) {
      this.logger.error(`Error generating prompt for template ${templateId}:`, error);
      throw new Error(`Failed to generate prompt: ${(error as Error).message}`);
    }
  }

  private preprocessParameters(template: AdvancedPromptTemplate, parameters: Record<string, string>): Record<string, string> {
    const processedParams = { ...parameters };
    switch (template.category) {
      case 'research':
        if (!processedParams.citationStyle && template.constraints?.citationStyle) {
          processedParams.citationStyle = template.constraints.citationStyle;
        }
        break;
      case 'visual':
        if (template.constraints?.maxWords && processedParams.scene) {
          const words = processedParams.scene.split(/\s+/);
          if (words.length > template.constraints.maxWords) {
            processedParams.scene = words.slice(0, template.constraints.maxWords).join(' ');
          }
        }
        break;
      case 'tone-transformation':
        if (!processedParams.toneMode && template.toneMode) {
          processedParams.toneMode = template.toneMode;
        }
        break;
    }
    return processedParams;
  }

  private postprocessPrompt(template: AdvancedPromptTemplate, prompt: string): string {
    let processedPrompt = prompt;
    if (template.constraints) {
      if (template.constraints.maxWords) {
        const words = processedPrompt.split(/\s+/);
        if (words.length > template.constraints.maxWords) {
          processedPrompt = words.slice(0, template.constraints.maxWords).join(' ');
        }
      }
      if (template.constraints.disallowedTerms) {
        for (const term of template.constraints.disallowedTerms) {
          processedPrompt = processedPrompt.replace(new RegExp(term, 'gi'), '[redacted]');
        }
      }
      if (template.constraints.requiredTerms) {
        for (const term of template.constraints.requiredTerms) {
          if (!processedPrompt.includes(term)) {
            processedPrompt += `\n\nNote: This prompt requires the term "${term}".`;
          }
        }
      }
    }
    if (template.outputVerification) {
      if (template.outputVerification.requiresCitations) {
        processedPrompt += '\n\nNote: Include citations for all factual claims in your response.';
      }
      if (template.outputVerification.confidenceThreshold) {
        processedPrompt += `\n\nNote: Indicate your confidence level for each claim. Only include claims with confidence >= ${template.outputVerification.confidenceThreshold}%.`;
      }
    }
    return processedPrompt;
  }

  private validateTemplateStructure(template: AdvancedPromptTemplate): void {
    const issues: string[] = [];
    if (!template.formatFnTemplate) {
      issues.push('Missing formatFnTemplate');
    }
    if (!template.parameters || template.parameters.length === 0) {
      issues.push('No parameters defined');
    }
    if (!template.reasoningModes || template.reasoningModes.length === 0) {
      issues.push('No reasoning modes defined');
    }
    switch (template.category) {
      case 'research':
        if (!template.reasoningModes.some(mode =>
          ['retrieval-augmented', 'source-anchors', 'evidence-ranking'].includes(mode))) {
          issues.push('Research template should include at least one research-specific reasoning mode');
        }
        break;
      case 'visual':
        if (!template.reasoningModes.includes('visual-decomposition')) {
          issues.push('Visual template should include visual-decomposition reasoning mode');
        }
        break;
      case 'tone-transformation':
        if (!template.toneMode) {
          issues.push('Tone transformation template should specify a toneMode');
        }
        break;
    }
    if (issues.length > 0) {
      this.logger.warn(`Template ${template.id} has structural issues: ${issues.join(', ')}`);
    }
  }

  clear(): void {
    this.templates.clear();
    this.logger.info('Cleared all templates');
  }
}

export const promptService = new PromptService();
