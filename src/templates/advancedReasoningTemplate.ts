import { AdvancedPromptTemplate } from '../../types/promptTypes';

export const advancedReasoningTemplate: AdvancedPromptTemplate = {
  id: 'advanced-reasoning',
  title: 'Advanced Reasoning Framework',
  description: 'Multi-modal reasoning system for complex problem-solving with structured analytical approaches',
  version: '2.0',
  icon: 'psychology',
  color: '#7B1FA2',
  category: 'reasoning',
  parameters: [
    { 
      id: 'problem', 
      label: 'Problem Statement', 
      type: 'textarea', 
      required: true, 
      placeholder: 'Specify the problem, question, or scenario requiring analysis.' 
    },
    { 
      id: 'reasoningApproach', 
      label: 'Primary Reasoning Approach', 
      type: 'select', 
      options: [ 
        { value: 'chain-of-thought', label: 'Sequential Chain-of-Thought' },
        { value: 'tree-of-thought', label: 'Branching Tree-of-Thought' }, 
        { value: 'hypothesis-driven', label: 'Hypothesis Testing' },
        { value: 'first-principles', label: 'First Principles Analysis' },
        { value: 'socratic', label: 'Socratic Questioning' }
      ], 
      default: 'chain-of-thought', 
      required: true 
    },
    { 
      id: 'steps', 
      label: 'Minimum Reasoning Steps', 
      type: 'number', 
      default: '5', 
      required: false,
      helperText: 'Minimum number of distinct reasoning steps to apply'
    },
    { 
      id: 'hypothesis', 
      label: 'Initial Hypothesis', 
      type: 'textarea', 
      required: false, 
      placeholder: 'Optional starting hypothesis or assumption to test.' 
    },
    {
      id: 'domainConstraints',
      label: 'Domain-Specific Constraints',
      type: 'textarea',
      required: false,
      placeholder: 'Any domain-specific rules, boundaries, or assumptions that must be respected.'
    },
    {
      id: 'outputFormat',
      label: 'Output Structure',
      type: 'select',
      options: [
        { value: 'narrative', label: 'Narrative Analysis' },
        { value: 'structured', label: 'Structured Step-by-Step' },
        { value: 'dialectical', label: 'Thesis-Antithesis-Synthesis' },
        { value: 'decision-tree', label: 'Decision Tree Format' }
      ],
      default: 'structured',
      required: false
    }
  ],
  reasoningModes: [
    'chain-of-thought', 
    'tree-of-thought', 
    'hypothesis-driven', 
    'self-reflection',
    'adversarial-critique',
    'self-consistency'
  ],
  formatFnTemplate: `# Advanced Reasoning Analysis Framework

## Problem Statement
{{problem}}

## Reasoning Approach
{{#select reasoningApproach value="chain-of-thought"}}
I will apply **Sequential Chain-of-Thought** reasoning:
- Break down the problem into a sequence of logical steps
- Each step will build on previous insights
- Maintain linear progression toward the solution
- Highlight dependencies between steps
- Resolve any conflicting implications
{{/select}}

{{#select reasoningApproach value="tree-of-thought"}}
I will apply **Branching Tree-of-Thought** reasoning:
- Map multiple possible solution pathways
- Explore divergent lines of reasoning in parallel
- Evaluate the promise of each branch using explicit criteria
- Prune less promising paths after sufficient exploration
- Synthesize insights from multiple branches
{{/select}}

{{#select reasoningApproach value="hypothesis-driven"}}
I will apply **Hypothesis Testing** reasoning:
- Start with the initial hypothesis: {{#if hypothesis}}{{hypothesis}}{{else}}[To be formulated after initial analysis]{{/if}}
- Generate multiple competing hypotheses that could explain the situation
- Identify critical evidence that would distinguish between hypotheses
- Evaluate available information against each hypothesis
- Update confidence levels based on evidence strength
- Resolve toward most supported conclusion
{{/select}}

{{#select reasoningApproach value="first-principles"}}
I will apply **First Principles Analysis**:
- Identify fundamental truths or axioms that cannot be deduced from other propositions
- Decompose the problem into basic elements
- Avoid assumptions based on analogy or convention
- Rebuild solution from foundational principles
- Test reconstruction against original problem statement
{{/select}}

{{#select reasoningApproach value="socratic"}}
I will apply **Socratic Questioning**:
- Probe assumptions underlying the problem
- Seek clarification on fundamental concepts
- Challenge implications and consequences
- Question the question itself
- Explore alternative perspectives and frameworks
- Synthesize insights from dialectical exploration
{{/select}}

{{#if domainConstraints}}
## Domain Constraints
The following constraints will be respected throughout the analysis:
{{domainConstraints}}
{{/if}}

## Reasoning Process

{{#select outputFormat value="narrative"}}
I'll present a narrative analysis that walks through the reasoning process in a cohesive, flowing form. This will maintain readability while preserving logical rigor.
{{/select}}

{{#select outputFormat value="structured"}}
I'll use a highly structured approach with numbered steps:

{{/select}}

{{#select outputFormat value="dialectical"}}
I'll use a dialectical approach:
1. **THESIS** - Initial position based on primary evidence
2. **ANTITHESIS** - Counter-position challenging the thesis
3. **SYNTHESIS** - Resolution that addresses the strengths and weaknesses of both positions
{{/select}}

{{#select outputFormat value="decision-tree"}}
I'll structure the analysis as a decision tree:
- Key Decision Points (KDPs) that branch the analysis
- Criteria for evaluating each path
- Consequences and follow-on decisions for each branch
- Final recommendation with path tracing
{{/select}}

### Analytical Steps (Minimum {{steps}} steps)
I'll break down the reasoning into at least {{steps}} distinct analytical steps, each building toward the solution.

### Critical Reflection
After completing the initial analysis, I'll apply:
1. Self-consistency check: Looking for internal contradictions
2. Adversarial critique: Identifying the strongest counter-arguments
3. Confidence assessment: Evaluating certainty levels for key conclusions

## Final Synthesis and Conclusion
The analysis will conclude with a clear synthesis of key insights and a direct answer to the original problem.`,
  outputFormat: 'markdown',
  constraints: { 
    tokenBudget: 4000,
    minWords: 300,
    maxWords: 3000,
    requiredTerms: ['analysis', 'reasoning', 'conclusion']
  },
  outputVerification: {
    confidenceThreshold: 70,
    validateStructure: true,
    minWords: 300
  },
  examples: [
    {
      input: { 
        problem: 'What strategy should a traditional retail business adopt to compete with e-commerce giants?', 
        reasoningApproach: 'tree-of-thought', 
        steps: '6',
        outputFormat: 'structured'
      },
      output: '(Structured analysis exploring multiple competitive strategy branches, evaluating omnichannel, specialization, and experience-based approaches)'
    },
    {
      input: {
        problem: 'Is consciousness an emergent property of complex neural networks, or something fundamentally different?',
        reasoningApproach: 'hypothesis-driven',
        hypothesis: 'Consciousness is an emergent property that arises when information processing systems reach a certain threshold of complexity.',
        outputFormat: 'dialectical'
      },
      output: '(Dialectical analysis comparing emergent vs non-emergent theories of consciousness with thesis-antithesis-synthesis structure)'
    }
  ]
};