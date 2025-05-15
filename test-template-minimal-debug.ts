import { promptService } from './src';
import { advancedReasoningTemplate } from './src/templates/advancedReasoningTemplate';
import { counterfactualTemplate } from './src/templates/counterfactualTemplate';
import { pentagramVisualTemplate } from './src/templates/pentagramVisualTemplate';
import { satiricalVoiceTemplate } from './src/templates/satiricalVoiceTemplate';
import { deepResearchTemplate } from './src/templates/deepResearchTemplate';

function tryRegister(template: any) {
  try {
    Object.entries(template).forEach(([key, val]) => {
      if (val === undefined) throw new Error(`Template ${template.id} has undefined value for ${key}`);
    });
    promptService.registerTemplate(template);
    console.log(`Registered: ${template.id}`);
  } catch (err) {
    console.error(`❌ Failed to register template ${template.id}:`, err);
  }
}

// Register each template individually for isolation
type TemplateEntry = [string, any];
const templates: TemplateEntry[] = [
  ['advancedReasoningTemplate', advancedReasoningTemplate],
  ['counterfactualTemplate', counterfactualTemplate],
  ['pentagramVisualTemplate', pentagramVisualTemplate],
  ['satiricalVoiceTemplate', satiricalVoiceTemplate],
  ['deepResearchTemplate', deepResearchTemplate],
];

for (const [name, template] of templates) {
  console.log(`\n--- Testing ${name} ---`);
  tryRegister(template);
}
