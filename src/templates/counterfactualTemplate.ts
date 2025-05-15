import { AdvancedPromptTemplate } from '../../types/promptTypes';

export const counterfactualTemplate: AdvancedPromptTemplate = {
  id: 'counterfactual-analysis',
  title: 'Counterfactual Analysis Framework',
  description: 'Systematically explore alternative scenarios and causal relationships through rigorous counterfactual reasoning',
  version: '2.0',
  icon: 'timeline',
  color: '#0288D1',
  category: 'analysis',
  parameters: [
    { 
      id: 'baseline', 
      label: 'Factual Baseline', 
      type: 'textarea', 
      required: true, 
      placeholder: 'Describe the actual historical events, decisions, or current state of affairs.' 
    },
    { 
      id: 'counterfactual', 
      label: 'Counterfactual Intervention', 
      type: 'textarea', 
      required: true, 
      placeholder: 'Specify the precise change, intervention, or alternative decision to analyze.' 
    },
    {
      id: 'timeframe',
      label: 'Analysis Timeframe',
      type: 'select',
      options: [
        { value: 'immediate', label: 'Immediate effects (days/weeks)' },
        { value: 'short', label: 'Short-term effects (months)' },
        { value: 'medium', label: 'Medium-term effects (1-5 years)' },
        { value: 'long', label: 'Long-term effects (5+ years)' },
        { value: 'multi', label: 'Multi-timeframe analysis (immediate to long-term)' }
      ],
      default: 'medium',
      required: true
    },
    { 
      id: 'domains', 
      label: 'Impact Domains', 
      type: 'textarea', 
      required: false, 
      placeholder: 'Specific areas to analyze (e.g., economic, social, technological). Leave blank for comprehensive analysis.' 
    },
    {
      id: 'causalDepth',
      label: 'Causal Analysis Depth',
      type: 'select',
      options: [
        { value: 'first', label: 'First-order effects only' },
        { value: 'second', label: 'First and second-order effects' },
        { value: 'network', label: 'Causal network analysis' },
        { value: 'feedback', label: 'Full system with feedback loops' }
      ],
      default: 'second',
      required: false
    },
    {
      id: 'uncertaintyHandling',
      label: 'Uncertainty Approach',
      type: 'select',
      options: [
        { value: 'qualitative', label: 'Qualitative assessment (low/medium/high)' },
        { value: 'probabilistic', label: 'Probabilistic reasoning with estimates' },
        { value: 'scenarios', label: 'Multiple scenario branches' },
        { value: 'bayesian', label: 'Bayesian confidence updating' }
      ],
      default: 'qualitative',
      required: false
    },
    {
      id: 'outputFormat',
      label: 'Output Format',
      type: 'select',
      options: [
        { value: 'narrative', label: 'Narrative analysis' },
        { value: 'causal-map', label: 'Causal mapping diagram' },
        { value: 'decision-tree', label: 'Decision tree with branches' },
        { value: 'timeline', label: 'Comparative timeline' },
        { value: 'matrix', label: 'Comparison matrix' }
      ],
      default: 'narrative',
      required: true
    }
  ],
  reasoningModes: [
    'causal-chain-mapping',
    'tree-of-thought',
    'bayesian-update',
    'feedback-modeling',
    'hypothesis-driven',
    'self-reflection'
  ],
  formatFnTemplate: `# Counterfactual Analysis Framework

## Initial Conditions

### Factual Baseline
{{baseline}}

### Counterfactual Intervention
{{counterfactual}}

### Analysis Parameters
- **Timeframe**: {{timeframe}}
- **Causal Analysis Depth**: {{causalDepth}}
- **Uncertainty Approach**: {{uncertaintyHandling}}
{{#if domains}}
- **Impact Domains**: {{domains}}
{{/if}}

## Methodological Framework

### Causal Analysis Architecture

{{#select causalDepth value="first"}}
I'll apply **First-order Effects Analysis**:
- Direct causal outcomes from the counterfactual intervention
- Immediate consequences that follow with high certainty
- Primary impact assessment without cascade effects
{{/select}}

{{#select causalDepth value="second"}}
I'll apply **First and Second-order Effects Analysis**:
- Primary effects directly from the counterfactual change
- Secondary effects emerging from the primary consequences
- Two-level causal chain mapping with distinction between levels
{{/select}}

{{#select causalDepth value="network"}}
I'll apply **Causal Network Analysis**:
- Comprehensive mapping of interconnected causal pathways
- Multi-node influence tracking across system elements
- Identification of key causal junctures and decision points
- Analysis of pathway interdependencies and relative strengths
{{/select}}

{{#select causalDepth value="feedback"}}
I'll apply **Full System Analysis with Feedback Loops**:
- Complete causal network mapping with:
  - Reinforcing feedback loops (amplifying effects)
  - Balancing feedback loops (stabilizing effects)
  - Time delays and accumulation effects
  - System adaptation and emergent properties
- Identification of regime shifts and tipping points
{{/select}}

### Temporal Scope Analysis

{{#select timeframe value="immediate"}}
I'll focus on **Immediate Effects** (days/weeks):
- Rapid direct consequences of the intervention
- Initial system responses and adaptations
- Crisis or rapid adjustment dynamics
- Limited to short-term horizons without structural changes
{{/select}}

{{#select timeframe value="short"}}
I'll focus on **Short-term Effects** (months):
- Initial adaptations and adjustments to the change
- Early-stage consequences before system restructuring
- Transitional dynamics and emerging patterns
- Limited institutional or structural modifications
{{/select}}

{{#select timeframe value="medium"}}
I'll focus on **Medium-term Effects** (1-5 years):
- Substantial system adaptations and responses
- Significant behavioral and institutional adjustments
- Emergence of new equilibria and patterns
- Partial structural transformations in affected systems
{{/select}}

{{#select timeframe value="long"}}
I'll focus on **Long-term Effects** (5+ years):
- Deep structural and systemic transformations
- Fundamental shifts in equilibria and organizing principles
- Full adaptation cycles and regime transitions
- Emergent system properties and path dependencies
{{/select}}

{{#select timeframe value="multi"}}
I'll conduct a **Multi-timeframe Analysis** spanning:
1. Immediate effects (days/weeks): Initial shocks and reactions
2. Short-term effects (months): Early adaptations and adjustments
3. Medium-term effects (1-5 years): System reconfiguration and new patterns
4. Long-term effects (5+ years): Structural transformation and equilibrium shifts

This will capture the full temporal evolution of consequences across different time horizons.
{{/select}}

### Uncertainty Management Approach

{{#select uncertaintyHandling value="qualitative"}}
I'll use **Qualitative Uncertainty Assessment**:
- Each outcome will be assigned a confidence level (Low/Medium/High)
- Clear distinction between well-established and speculative consequences
- Transparency about knowledge limitations and assumptions
- Identification of critical uncertainties affecting outcomes
{{/select}}

{{#select uncertaintyHandling value="probabilistic"}}
I'll use **Probabilistic Reasoning**:
- Approximate probability ranges for key outcomes (e.g., 60-80%)
- Explicit distinction between high and low confidence projections
- Identification of factors that could shift probabilities
- Discussion of the basis for probability estimates
{{/select}}

{{#select uncertaintyHandling value="scenarios"}}
I'll use **Multiple Scenario Branches**:
- Development of distinct scenario paths based on key uncertainties
- Exploration of multiple possible outcome trajectories
- Comparison of requirements for different scenarios to manifest
- Analysis of early indicators that would signal which scenario is unfolding
{{/select}}

{{#select uncertaintyHandling value="bayesian"}}
I'll use **Bayesian Confidence Updating**:
- Initial confidence estimates based on prior knowledge
- Explicit updating of confidence based on logical implications
- Conditional probability assessment for interconnected outcomes
- Tracking of compounding uncertainty across causal chains
{{/select}}

{{#if domains}}
### Domain-Specific Analysis
I'll analyze impacts across these specific domains:
{{domains}}
{{else}}
### Comprehensive Domain Analysis
I'll analyze impacts across all relevant domains, including:
- Economic/Financial implications
- Social/Cultural effects
- Political/Governance consequences
- Technological developments
- Environmental impacts
- Institutional adaptations
{{/if}}

## Analysis Output

{{#select outputFormat value="narrative"}}
### Narrative Analysis
I'll provide a detailed narrative exploration of how events would likely unfold in the counterfactual scenario, structured chronologically and by impact domains. The narrative will explicitly compare the counterfactual timeline with the actual baseline at key divergence points.
{{/select}}

{{#select outputFormat value="causal-map"}}
### Causal Mapping Diagram
I'll present the analysis as a structured causal map showing:
- The counterfactual intervention as the central node
- Primary causal pathways stemming from the intervention
- Secondary and tertiary effects with causal links
- Feedback loops and interaction effects
- Uncertainty levels for different pathways
- Comparative elements showing divergence from baseline reality
{{/select}}

{{#select outputFormat value="decision-tree"}}
### Decision Tree Analysis
I'll structure the analysis as a decision tree showing:
- The counterfactual intervention as the initial branch point
- Key subsequent decision points and contingencies
- Major outcome branches with probability assessments
- Critical factors determining path selection
- Terminal outcomes and their implications
- Comparison with the baseline decision path
{{/select}}

{{#select outputFormat value="timeline"}}
### Comparative Timeline
I'll create parallel timelines showing:
- The baseline factual sequence of events
- The counterfactual alternative sequence
- Key divergence points and their causal significance
- Comparative outcomes at equivalent time points
- Convergence or divergence patterns over time
- Critical junctures and path dependency effects
{{/select}}

{{#select outputFormat value="matrix"}}
### Comparison Matrix
I'll develop a structured matrix comparing:
- Key metrics and outcomes between baseline and counterfactual
- Impact magnitudes across different domains
- Temporal evolution of effects (immediate to long-term)
- Certainty levels for different comparison elements
- Winners and losers in each scenario
- System-level differences and implications
{{/select}}

## Analytical Process
1. **Baseline Mapping**: Establish key features and dynamics of the factual scenario
2. **Counterfactual Intervention Analysis**: Precisely define the nature and scope of the change
3. **Causal Propagation Modeling**: Trace effects through the system using the specified depth approach
4. **Temporal Evolution Analysis**: Track developments across the defined timeframe
5. **Domain Impact Assessment**: Evaluate consequences across all relevant domains
6. **Confidence and Uncertainty Evaluation**: Apply the specified uncertainty approach
7. **Comparative Assessment**: Systematically compare counterfactual and baseline outcomes
8. **Meta-analysis**: Reflect on methodological limitations and alternative interpretations

## Conclusion Framework
The analysis will conclude with:
1. **Key Insights**: The most significant findings from the counterfactual analysis
2. **Critical Uncertainties**: The most important unknowns affecting the conclusions
3. **Implications**: The significance of the analysis for understanding causality in this context
4. **Methodological Reflection**: Limitations of the counterfactual approach in this case`,
  outputFormat: 'markdown',
  constraints: {
    maxWords: 3000,
    disallowedTerms: ['impossible to know', 'cannot be determined', 'pure speculation']
  },
  outputVerification: {
    validateStructure: true,
    confidenceThreshold: 60
  },
  examples: [
    {
      input: { 
        baseline: 'The 2008 financial crisis occurred, leading to the Great Recession, massive bailouts, and new financial regulations.',
        counterfactual: 'Lehman Brothers was bailed out by the government in September 2008 instead of being allowed to fail.',
        timeframe: 'multi',
        causalDepth: 'feedback',
        uncertaintyHandling: 'scenarios',
        outputFormat: 'timeline'
      },
      output: '(Comparative timeline analysis of financial system evolution with vs. without Lehman failure, showing immediate market stabilization but potentially greater moral hazard and different regulatory outcomes)'
    },
    {
      input: {
        baseline: 'Company X implemented a remote-first work policy in 2020 during the pandemic and has maintained it since.',
        counterfactual: 'Company X required all employees to return to the office full-time in January 2021.',
        timeframe: 'medium',
        domains: 'Employee retention, productivity, corporate culture, real estate costs, talent acquisition',
        causalDepth: 'second',
        uncertaintyHandling: 'qualitative',
        outputFormat: 'matrix'
      },
      output: '(Comparison matrix analyzing differences between remote-first and return-to-office policies across specified domains with qualitative uncertainty assessments)'
    }
  ]
};