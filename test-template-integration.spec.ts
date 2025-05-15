import { describe, it, expect } from 'vitest';
import { promptService } from './src';
import { advancedReasoningTemplate } from './src/templates/advancedReasoningTemplate';
import { counterfactualTemplate } from './src/templates/counterfactualTemplate';
import { pentagramVisualTemplate } from './src/templates/pentagramVisualTemplate';
import { satiricalVoiceTemplate } from './src/templates/satiricalVoiceTemplate';
import { deepResearchTemplate } from './src/templates/deepResearchTemplate';

const templateExpectations: Record<string, string> = {
  advancedReasoningTemplate: '# Advanced Reasoning Analysis Framework',
  counterfactualTemplate: '# Counterfactual Analysis Framework',
  pentagramVisualTemplate: '# Pentagram Visual Analysis System',
  satiricalVoiceTemplate: '# Satirical Voice Transformation System',
  deepResearchTemplate: '# Deep Research Investigation',
};

describe('MindMeld Template Integration', () => {
  const templateList = [
    { name: 'advancedReasoningTemplate', template: advancedReasoningTemplate },
    { name: 'counterfactualTemplate', template: counterfactualTemplate },
    { name: 'pentagramVisualTemplate', template: pentagramVisualTemplate },
    { name: 'satiricalVoiceTemplate', template: satiricalVoiceTemplate },
    { name: 'deepResearchTemplate', template: deepResearchTemplate },
  ];

  templateList.forEach(({ name, template }) => {
    it(`registers and generates prompt for ${name}`, () => {
      promptService.clear();
      promptService.registerTemplate(template);
      const params: Record<string, string> = {};
      template.parameters.forEach((p) => {
        if (p.required) params[p.id] = p.options?.[0]?.value || 'test';
      });
      const prompt = promptService.generatePrompt(template.id, params, { enforceConstraints: false });
      expect(prompt).toContain(templateExpectations[name]);
    });

    it(`fails validation for missing required params in ${name}`, () => {
      promptService.clear();
      promptService.registerTemplate(template);
      expect(() => promptService.generatePrompt(template.id, {}, { enforceConstraints: true })).toThrow();
    });

    it(`handles edge cases for ${name}`, () => {
      promptService.clear();
      promptService.registerTemplate(template);
      const params: Record<string, string> = {};
      template.parameters.forEach((p) => {
        if (p.required) {
          // Edge: very long string
          params[p.id] = 'x'.repeat(1000);
        }
      });
      const prompt = promptService.generatePrompt(template.id, params, { enforceConstraints: false });
      expect(typeof prompt).toBe('string');
      expect(prompt.length).toBeGreaterThan(0);
    });
  });
});

// Template quirks:
// - advancedReasoningTemplate: formatFnTemplate heading does not match title property (uses "Analysis Framework").
// - All templates: required parameters are enforced, and prompt output always starts with a Markdown heading.
