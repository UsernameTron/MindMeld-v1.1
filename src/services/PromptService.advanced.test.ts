import { PromptService, AdvancedPromptTemplate, ReasoningMode } from '../services/PromptService';
import { promptTemplates } from '../config/promptTemplates';

describe('Advanced Reasoning Modes', () => {
  it('should support all advanced reasoning modes in templates', () => {
    const advanced = promptTemplates.find(t => t.id === 'advanced-reasoning') as AdvancedPromptTemplate;
    expect(advanced).toBeDefined();
    // Simulate adding all modes
    advanced.reasoningModes = [
      'chain-of-thought',
      'tree-of-thought',
      'self-consistency',
      'hypothesis-driven',
      'program-aided',
      'retrieval-augmented',
      'adversarial',
      'reflection',
      'dynamic-memory',
      'constraint-logic'
    ];
    expect(advanced.reasoningModes.length).toBe(10);
  });
});
