export interface PromptParameter {
  id: string;
  label: string;
  type: 'text' | 'select' | 'textarea';
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  default?: string;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  parameters: PromptParameter[];
  format: (params: Record<string, string>) => string;
}

// Feature flag map for template enable/disable
export const templateFeatureFlags: Record<string, boolean> = {
  'deep-research': true,
  'advanced-reasoning': true,
  'counterfactual': true,
  'satirical-voice': true,
  'pentagram-visual': true,
};

// Only export enabled templates for registration
export const promptTemplates: PromptTemplate[] = [
  {
    id: 'deep-research',
    name: 'Deep Research',
    description: 'Comprehensive research with structured outputs and citations',
    icon: 'search',
    color: '#4285F4', // Google blue
    parameters: [
      {
        id: 'topic',
        label: 'Research Topic',
        type: 'text',
        placeholder: 'Enter the topic to research'
      },
      {
        id: 'depth',
        label: 'Research Depth',
        type: 'select',
        options: [
          { value: 'overview', label: 'Overview' },
          { value: 'standard', label: 'Standard' },
          { value: 'academic', label: 'Academic' }
        ],
        default: 'standard'
      }
      // More parameters will be added
    ],
    format: (params) => `# Deep Research Request: ${params.topic}

## Research Approach
- Conduct ${params.depth} research with multiple perspectives
- Include relevant statistics, examples, and context
- Consider historical context, current state, and future trends
- Address potential counterarguments or limitations
- Summarize key takeaways and provide citations

## Topic
${params.topic}`
  },
  {
    id: 'advanced-reasoning',
    name: 'Advanced Reasoning',
    description: 'Complex problem-solving with step-by-step reasoning chains',
    icon: 'brain',
    color: '#EA4335', // Google red
    parameters: [
      {
        id: 'problem',
        label: 'Problem Statement',
        type: 'textarea',
        placeholder: 'Describe the problem that needs reasoning'
      },
      {
        id: 'reasoningStyle',
        label: 'Reasoning Style',
        type: 'select',
        options: [
          { value: 'chain', label: 'Chain-of-Thought' },
          { value: 'tree', label: 'Tree-of-Thought' },
          { value: 'hypothetical', label: 'Hypothesis-Driven' },
          { value: 'verification', label: 'Self-Verification Loop' }
        ],
        default: 'chain'
      },
      {
        id: 'format',
        label: 'Output Format',
        type: 'select',
        options: [
          { value: 'narrative', label: 'Narrative' },
          { value: 'structured', label: 'Structured Steps' },
          { value: 'academic', label: 'Academic Format' }
        ],
        default: 'structured'
      }
    ],
    format: (params) => {
      const styleGuide = {
        chain: 'Break down the problem into sequential steps and solve it linearly',
        tree: 'Explore multiple solution pathways and compare outcomes',
        hypothetical: 'Formulate and test competing hypotheses',
        verification: 'Develop an answer, then critically review it'
      };
      
      return `# Advanced Reasoning Problem\n\n## Problem Statement\n${params.problem}\n\n## Reasoning Approach\n- Use ${params.reasoningStyle} reasoning: ${styleGuide[params.reasoningStyle as keyof typeof styleGuide]}\n- Present findings in ${params.format} format\n- Show all steps of your thinking process\n- Distinguish between facts, inferences, and assumptions\n- Conclude with clear, actionable insights\n\n## Analysis Instructions\n1. Define key terms and clarify assumptions\n2. Break the problem into component parts\n3. Apply systematic reasoning\n4. Validate conclusions with evidence\n5. Consider limitations of the analysis`;
    }
  },
  {
    id: 'counterfactual-analysis',
    name: 'Counterfactual Analysis',
    description: 'Explore alternative scenarios and outcomes',
    icon: 'git-branch',
    color: '#FBBC04', // Google yellow
    parameters: [
      {
        id: 'baseline',
        label: 'Actual Baseline',
        type: 'textarea',
        placeholder: 'What really happened / current state'
      },
      {
        id: 'counterfactual',
        label: 'Counterfactual Change',
        type: 'textarea',
        placeholder: 'What alternative scenario do you want to explore?'
      },
      {
        id: 'timeframe',
        label: 'Scope Window',
        type: 'text',
        placeholder: 'Time frame or logical span (e.g., "5 years" or "product lifecycle")'
      }
    ],
    format: (params) => `# Counterfactual Analysis\n\n## Actual Baseline\n${params.baseline}\n\n## Counterfactual Change\n${params.counterfactual}\n\n## Scope Window\n${params.timeframe}\n\n## Analysis Instructions\n1. Map first-order effects of the change\n2. Branch major plausible pathways\n3. Capture recursive loops or delayed impacts\n4. Compare actual vs. counterfactual across relevant metrics\n5. Present assumptions, caveats, and confidence levels`
  },
  {
    id: 'visual-prompt',
    name: 'Visual Prompt Generator',
    description: 'Create prompts for image generation',
    icon: 'image',
    color: '#34A853', // Google green
    parameters: [
      {
        id: 'scene',
        label: 'Scene Description',
        type: 'textarea',
        placeholder: 'Describe the image you want to generate'
      },
      {
        id: 'style',
        label: 'Visual Style',
        type: 'select',
        options: [
          { value: 'photorealistic', label: 'Photorealistic' },
          { value: 'anime', label: 'Anime/Manga' },
          { value: 'painting', label: 'Digital Painting' },
          { value: 'surreal', label: 'Surrealistic' }
        ],
        default: 'photorealistic'
      },
      {
        id: 'mood',
        label: 'Mood/Atmosphere',
        type: 'select',
        options: [
          { value: 'bright', label: 'Bright and Cheerful' },
          { value: 'dark', label: 'Dark and Moody' },
          { value: 'serene', label: 'Calm and Serene' },
          { value: 'dramatic', label: 'Dramatic and Intense' }
        ],
        default: 'bright'
      }
    ],
    format: (params) => `${params.scene}, ${params.style} style, ${params.mood} atmosphere, high detail, 8K resolution`
  }
].filter(t => templateFeatureFlags[t.id] !== false);
