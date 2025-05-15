import {
  promptService,
  advancedReasoningTemplate,
  deepResearchTemplate,
  counterfactualTemplate,
  pentagramVisualTemplate,
  satiricalVoiceTemplate
} from '../src';

function logPrompt(id: string, params: Record<string, string>) {
  try {
    const prompt = promptService.generatePrompt(id, params);
    console.log(`\n[${id}] Prompt length:`, prompt.length);
    console.log('Sample:', prompt.substring(0, 200) + '...');
  } catch (e) {
    console.error(`Error generating prompt for ${id}:`, e.message);
  }
}

console.log('Registering templates...');
promptService.clear();
promptService.registerTemplate(advancedReasoningTemplate);
promptService.registerTemplate(deepResearchTemplate);
promptService.registerTemplate(counterfactualTemplate);
promptService.registerTemplate(pentagramVisualTemplate);
promptService.registerTemplate(satiricalVoiceTemplate);

console.log('Registered templates:', promptService.getAllTemplates().map(t => t.id));

logPrompt('advanced-reasoning', {
  problem: 'How might renewable energy sources be effectively integrated into existing power grids?',
  steps: '5',
  hypothesis: 'Storage is the main challenge.'
});

logPrompt('deep-research', {
  topic: 'What are the long-term effects of remote work on urban economies?',
  recency: '3',
  sourceTypes: 'mixed',
  format: 'report'
});

logPrompt('counterfactual-analysis', {
  scenario: 'Company adopted remote work in 2020.',
  counterfactual: 'Company did not adopt remote work.',
  focus: 'Productivity'
});

logPrompt('pentagram-visual', {
  scene: 'A bustling city square at sunset.',
  style: 'infographic'
});

logPrompt('satirical-voice', {
  subject: 'Artificial Intelligence in daily life',
  target: 'Smart refrigerators',
  length: 'short'
});
