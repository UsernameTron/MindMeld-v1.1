// Base interface for backward compatibility
export interface BasePrompt {
  id: string;
  title: string;
  description: string;
}

// Parameter definition for complex templates
export interface PromptParameter {
  id: string;
  label: string;
  type: 'text' | 'select' | 'textarea' | 'number' | 'boolean';
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  default?: string;
  required?: boolean;
  helperText?: string;
}

// Reasoning mode type
export type ReasoningMode = 
  | 'chain-of-thought'
  | 'tree-of-thought'
  | 'retrieval-augmented'
  | 'program-aided'
  | 'adversarial-critique'
  | 'self-reflection'
  | 'hypothesis-driven'
  | 'statistical-validation'
  | 'self-consistency'
  | 'causal-chain-mapping'
  | 'bayesian-update'
  | 'feedback-modeling'
  | 'visual-decomposition'
  | 'prompt-synthesis';

// Output verification for advanced templates
export interface OutputVerification {
  requiresCitations?: boolean;
  confidenceThreshold?: number;
  [key: string]: any;
}

// Template constraints for advanced templates
export interface TemplateConstraints {
  tokenBudget?: number;
  sourceFilters?: string[];
  maxWords?: number;
  requiredTerms?: string[];
  disallowedTerms?: string[];
  citationStyle?: string;
  [key: string]: any;
}

// Template category, output format, and tone mode types
export type TemplateCategory =
  | 'research'
  | 'reasoning'
  | 'analysis'
  | 'creative'
  | 'visual'
  | 'tone-transformation';

export type OutputFormat =
  | 'summary'
  | 'report'
  | 'comparative'
  | 'markdown'
  | 'json';

export type ToneMode =
  | 'formal'
  | 'informal'
  | 'satirical'
  | 'neutral'
  | 'high-satire'
  | 'strategic-snark'
  | 'soft-roast'
  | 'deadpan'
  | 'socratic';

// Enhanced template interface
export interface AdvancedPromptTemplate extends BasePrompt {
  version: '2.0';
  icon: string;
  color: string;
  category: TemplateCategory;
  parameters: PromptParameter[];
  reasoningModes: ReasoningMode[];
  formatFnTemplate: string; // Template string for formatting
  outputFormat?: OutputFormat;
  toneMode?: ToneMode;
  constraints?: TemplateConstraints;
  outputVerification?: OutputVerification;
  styleMandatory?: string[];
  styleForbidden?: string[];
  behaviorSwitches?: Record<string, string> | string[];
  examples?: { input: Record<string, string>; output: string }[];
  templateSource?: string;
}

// Union type to support both formats
export type PromptTemplate = BasePrompt | AdvancedPromptTemplate;

// Runtime format function type
export type FormatFunction = (params: Record<string, string>) => string;

// Helper to check if a template is advanced
export function isAdvancedTemplate(template: PromptTemplate): template is AdvancedPromptTemplate {
  return 'version' in template && template.version === '2.0';
}
