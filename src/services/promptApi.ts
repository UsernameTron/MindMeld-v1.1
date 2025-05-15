import {
  promptService,
  PromptTemplate,
  AdvancedPromptTemplate
} from '../index';

export const promptApi = {
  getTemplates(): PromptTemplate[] {
    return promptService.getAllTemplates();
  },
  getTemplateById(id: string): PromptTemplate | undefined {
    return promptService.getTemplateById(id);
  },
  generatePrompt(templateId: string, params: Record<string, string>): string {
    try {
      return promptService.generatePrompt(templateId, params);
    } catch (e) {
      throw new Error(`Prompt generation failed: ${(e as Error).message}`);
    }
  }
};
