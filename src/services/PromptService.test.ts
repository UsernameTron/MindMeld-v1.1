import { PromptService, AdvancedPromptTemplate, ReasoningMode } from '../services/PromptService';
import { promptTemplates } from '../config/promptTemplates';

describe('PromptService', () => {
  const service = new PromptService(promptTemplates);

  it('should load all templates', () => {
    expect(service.getAllTemplates().length).toBeGreaterThan(0);
  });

  it('should get a template by id', () => {
    const t = service.getTemplateById('deep-research');
    expect(t).toBeDefined();
    expect(t?.id).toBe('deep-research');
  });

  it('should validate a valid template', () => {
    const t = service.getTemplateById('advanced-reasoning');
    expect(t && service.validateTemplate(t)).toBe(true);
  });

  it('should format a prompt with parameters', () => {
    const t = service.getTemplateById('visual-prompt');
    if (!t) throw new Error('Template not found');
    const result = service.formatPrompt('visual-prompt', {
      scene: 'A mountain at sunrise',
      style: 'painting',
      mood: 'serene'
    });
    expect(result).toContain('A mountain at sunrise');
    expect(result).toContain('painting style');
    expect(result).toContain('serene atmosphere');
  });

  it('should reject invalid templates', () => {
    const invalid = { id: '', name: '', description: '', icon: '', color: '', parameters: [], format: () => '' };
    expect(service.validateTemplate(invalid)).toBe(false);
  });
});
