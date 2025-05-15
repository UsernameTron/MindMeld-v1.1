import { promptService } from './services/promptService';
import { deepResearchTemplate } from './templates/deepResearch';

// Register a template
promptService.registerTemplate(deepResearchTemplate);

// Generate a prompt
const parameters = {
  topic: 'Impact of artificial intelligence on employment',
  recency: '3',
  sourceTypes: 'academic',
  format: 'report'
};

const prompt = promptService.generatePrompt('deep-research', parameters);
console.log(prompt);
