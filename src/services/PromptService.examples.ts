import { PromptService } from './PromptService';
import { promptTemplates } from '../config/promptTemplates';

// Example: Deep Research
const deepResearchPrompt = new PromptService(promptTemplates).formatPrompt('deep-research', {
  topic: 'The impact of quantum computing on cryptography',
  depth: 'academic'
});

// Example: Advanced Reasoning
const advancedReasoningPrompt = new PromptService(promptTemplates).formatPrompt('advanced-reasoning', {
  problem: 'How can urban areas reduce heat island effects?',
  reasoningStyle: 'tree',
  format: 'structured'
});

// Example: Counterfactual Analysis
const counterfactualPrompt = new PromptService(promptTemplates).formatPrompt('counterfactual-analysis', {
  baseline: 'The city banned cars in 2020',
  counterfactual: 'The city did not ban cars',
  timeframe: '2020-2025'
});

// Example: Visual Prompt
const visualPrompt = new PromptService(promptTemplates).formatPrompt('visual-prompt', {
  scene: 'A futuristic city skyline at dusk',
  style: 'surreal',
  mood: 'dramatic'
});

console.log({ deepResearchPrompt, advancedReasoningPrompt, counterfactualPrompt, visualPrompt });
