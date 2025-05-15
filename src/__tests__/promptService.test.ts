import { PromptService } from '../services/promptService';
import { formatPromptFromTemplate } from '../utils/promptFormatter';

// Mock the formatPromptFromTemplate function
jest.mock('../utils/promptFormatter', () => ({
  formatPromptFromTemplate: jest.fn((template, params) => `Mocked format: ${template.id}, Params: ${Object.keys(params).join(',')}`)
}));

describe('PromptService', () => {
  let service: PromptService;
  
  beforeEach(() => {
    service = new PromptService();
    // Reset mock counts
    (formatPromptFromTemplate as jest.Mock).mockClear();
  });
  
  test('registerTemplate adds templates to the service', () => {
    const basicTemplate = { id: 'basic', title: 'Basic', description: 'Basic template' };
    const advancedTemplate = {
      id: 'advanced',
      title: 'Advanced',
      description: 'Advanced template',
      version: '2.0',
      icon: 'star',
      color: '#000',
      category: 'research',
      parameters: [],
      reasoningModes: [],
      formatFnTemplate: 'Template'
    };
    
    // Feature flag respected in registerTemplate
    service.registerTemplate(basicTemplate);
    service.registerTemplate(advancedTemplate);
    
    expect(service.getAllTemplates().length).toBe(2);
    expect(service.getTemplateById('basic')).toBe(basicTemplate);
    expect(service.getTemplateById('advanced')).toBe(advancedTemplate);
  });
  
  test('getTemplatesByCategory filters templates by category', () => {
    const template1 = {
      id: 'template1',
      title: 'Template 1',
      description: 'Template 1',
      version: '2.0',
      icon: 'icon1',
      color: '#000',
      category: 'research',
      parameters: [],
      reasoningModes: [],
      formatFnTemplate: 'Template 1'
    };
    
    const template2 = {
      id: 'template2',
      title: 'Template 2',
      description: 'Template 2',
      version: '2.0',
      icon: 'icon2',
      color: '#000',
      category: 'analysis',
      parameters: [],
      reasoningModes: [],
      formatFnTemplate: 'Template 2'
    };
    
    service.registerTemplate(template1);
    service.registerTemplate(template2);
    
    const researchTemplates = service.getTemplatesByCategory('research');
    expect(researchTemplates.length).toBe(1);
    expect(researchTemplates[0].id).toBe('template1');
    
    const analysisTemplates = service.getTemplatesByCategory('analysis');
    expect(analysisTemplates.length).toBe(1);
    expect(analysisTemplates[0].id).toBe('template2');
  });
  
  test('generatePrompt for basic templates combines title and description', () => {
    const basicTemplate = { id: 'basic', title: 'Basic Title', description: 'Basic description' };
    service.registerTemplate(basicTemplate);
    
    const result = service.generatePrompt('basic', {});
    expect(result).toBe('Basic Title\n\nBasic description');
  });
  
  test('generatePrompt for advanced templates uses formatPromptFromTemplate', () => {
    const advancedTemplate = {
      id: 'advanced',
      title: 'Advanced',
      description: 'Advanced template',
      version: '2.0',
      icon: 'star',
      color: '#000',
      category: 'research',
      parameters: [],
      reasoningModes: [],
      formatFnTemplate: 'Template {{param}}'
    };
    
    service.registerTemplate(advancedTemplate);
    
    const params = { param: 'value' };
    service.generatePrompt('advanced', params);
    
    // Check if formatPromptFromTemplate was called with correct parameters
    expect(formatPromptFromTemplate).toHaveBeenCalledWith(advancedTemplate, params);
  });
  
  test('generatePrompt throws error for non-existent template', () => {
    expect(() => {
      service.generatePrompt('non-existent', {});
    }).toThrow('Template with ID non-existent not found');
  });
  
  test('clear removes all templates', () => {
    service.registerTemplate({ id: 'template1', title: 'Template 1', description: 'Template 1' });
    service.registerTemplate({ id: 'template2', title: 'Template 2', description: 'Template 2' });
    
    expect(service.getAllTemplates().length).toBe(2);
    
    service.clear();
    
    expect(service.getAllTemplates().length).toBe(0);
  });
});
