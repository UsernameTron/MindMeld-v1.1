import {
  promptService,
  advancedReasoningTemplate,
  deepResearchTemplate,
  counterfactualTemplate,
  pentagramVisualTemplate,
  satiricalVoiceTemplate
} from './src';

console.log('Registering templates...');
promptService.clear();
Object.entries(advancedReasoningTemplate).forEach(([key, val]) => {
  if (val === undefined) throw new Error(`advancedReasoningTemplate has undefined value for ${key}`);
});
promptService.registerTemplate(advancedReasoningTemplate);
// promptService.registerTemplate(deepResearchTemplate);
// promptService.registerTemplate(counterfactualTemplate);
// promptService.registerTemplate(pentagramVisualTemplate);
// promptService.registerTemplate(satiricalVoiceTemplate);

console.log('Registered templates:', promptService.getAllTemplates().map(t => t.id));

console.log('\nTesting Advanced Reasoning Template:');
const reasoningPrompt = promptService.generatePrompt('advanced-reasoning', {
  problem: 'How might renewable energy sources be effectively integrated into existing power grids?',
  steps: '5',
  hypothesis: 'Storage is the main challenge.'
});
console.log('Prompt length:', reasoningPrompt.length);
console.log('Sample:', reasoningPrompt.substring(0, 200) + '...');

console.log('\nTesting Deep Research Template:');
const researchPrompt = promptService.generatePrompt('deep-research', {
  topic: 'What are the long-term effects of remote work on urban economies?',
  recency: '3',
  sourceTypes: 'mixed',
  format: 'report'
});
console.log('Prompt length:', researchPrompt.length);
console.log('Sample:', researchPrompt.substring(0, 200) + '...');

console.log('\nTesting Counterfactual Template:');
const counterfactualPrompt = promptService.generatePrompt('counterfactual-analysis', {
  scenario: 'Company adopted remote work in 2020.',
  counterfactual: 'Company did not adopt remote work.',
  focus: 'Productivity'
});
console.log('Prompt length:', counterfactualPrompt.length);
console.log('Sample:', counterfactualPrompt.substring(0, 200) + '...');

console.log('\nTesting Pentagram Visual Template:');
const pentagramPrompt = promptService.generatePrompt('pentagram-visual', {
  scene: 'A bustling city square at sunset.',
  style: 'infographic'
});
console.log('Prompt length:', pentagramPrompt.length);
console.log('Sample:', pentagramPrompt.substring(0, 200) + '...');

console.log('\nTesting Satirical Voice Template:');
const satiricalPrompt = promptService.generatePrompt('satirical-voice', {
  subject: 'Artificial Intelligence in daily life',
  target: 'Smart refrigerators',
  length: 'short'
});
console.log('Prompt length:', satiricalPrompt.length);
console.log('Sample:', satiricalPrompt.substring(0, 200) + '...');
