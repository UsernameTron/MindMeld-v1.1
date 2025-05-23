import { AdvancedPromptTemplate } from '../../types/promptTypes';

export const deepResearchTemplate: AdvancedPromptTemplate = {
  id: 'deep-research',
  title: 'Deep Research Investigation',
  description: 'Conduct a comprehensive, multi-source research investigation with critical synthesis and citation.',
  version: '2.0',
  icon: 'search',
  color: '#6A1B9A',
  category: 'research',
  parameters: [
    { id: 'topic', label: 'Research Topic', type: 'textarea', required: true, placeholder: 'Describe the topic or question to investigate.' },
    { id: 'sources', label: 'Preferred Sources', type: 'textarea', required: false, placeholder: 'List any preferred sources, databases, or types of evidence.' },
    { id: 'depth', label: 'Depth of Analysis', type: 'select', options: [
      { value: 'overview', label: 'Overview (broad summary)' },
      { value: 'detailed', label: 'Detailed (in-depth analysis)' },
      { value: 'exhaustive', label: 'Exhaustive (all available evidence)' }
    ], default: 'detailed', required: true },
    { id: 'citationStyle', label: 'Citation Style', type: 'select', options: [
      { value: 'apa', label: 'APA' },
      { value: 'mla', label: 'MLA' },
      { value: 'chicago', label: 'Chicago' },
      { value: 'none', label: 'None' }
    ], default: 'apa', required: false }
  ],
  reasoningModes: [
    'retrieval-augmented',
    'chain-of-thought',
    'self-reflection',
    'statistical-validation',
    'adversarial-critique'
  ],
  formatFnTemplate: `# Deep Research Investigation\n\n## Research Topic\n{{topic}}\n\n## Methodology\n- Depth: {{depth}}\n{{#if sources}}- Preferred Sources: {{sources}}{{/if}}\n- Citation Style: {{citationStyle}}\n\n## Research Process\n1. Identify and collect relevant sources\n2. Critically evaluate credibility and relevance\n3. Synthesize findings across sources\n4. Highlight consensus, disagreements, and gaps\n5. Provide citations for all key claims\n\n## Findings\n[Detailed synthesis and analysis here]\n\n## References\n[Formatted citations according to selected style]`,
  outputFormat: 'markdown',
  constraints: {
    tokenBudget: 5000,
    minWords: 400,
    maxWords: 3500,
    requiredTerms: ['evidence', 'synthesis', 'citation']
  },
  outputVerification: {
    requiresCitations: true,
    confidenceThreshold: 80,
    validateStructure: true,
    minWords: 400
  },
  examples: [
    {
      input: {
        topic: 'The impact of remote work on productivity and employee well-being',
        sources: 'Peer-reviewed journals, government labor statistics, major news outlets',
        depth: 'detailed',
        citationStyle: 'apa'
      },
      output: '(Detailed synthesis of research on remote work, with citations in APA style)'
    },
    {
      input: {
        topic: 'The effectiveness of mindfulness interventions in education',
        depth: 'overview',
        citationStyle: 'mla'
      },
      output: '(Broad summary of evidence on mindfulness in education, with MLA citations)'
    }
  ]
};
