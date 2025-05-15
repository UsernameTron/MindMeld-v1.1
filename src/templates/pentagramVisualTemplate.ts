import { AdvancedPromptTemplate } from '../../types/promptTypes';

export const pentagramVisualTemplate: AdvancedPromptTemplate = {
  id: 'pentagram-visual',
  title: 'Pentagram Visual Analysis System',
  description: 'Decompose and analyze visual scenes, concepts, or compositions through a structured five-element framework',
  version: '2.0',
  icon: 'visibility',
  color: '#43A047',
  category: 'visual',
  parameters: [
    { 
      id: 'scene', 
      label: 'Visual Scene or Concept', 
      type: 'textarea', 
      required: true, 
      placeholder: 'Describe the visual scene, image, composition, or concept to analyze in detail.' 
    },
    {
      id: 'analysisMode',
      label: 'Analysis Framework',
      type: 'select',
      options: [
        { value: 'compositional', label: 'Compositional Elements (form, color, space, texture, movement)' },
        { value: 'narrative', label: 'Narrative Components (character, setting, action, symbol, mood)' },
        { value: 'conceptual', label: 'Conceptual Mapping (core concept, variations, context, implications, tensions)' },
        { value: 'emotional', label: 'Emotional Impact (primary emotion, intensity, contrast, resonance, subtext)' },
        { value: 'technical', label: 'Technical Execution (medium, technique, skill, innovation, constraints)' }
      ],
      default: 'compositional',
      required: true
    },
    {
      id: 'purpose',
      label: 'Analysis Purpose',
      type: 'select',
      options: [
        { value: 'description', label: 'Descriptive Analysis (what exists)' },
        { value: 'interpretation', label: 'Interpretive Analysis (meaning and significance)' },
        { value: 'evaluation', label: 'Evaluative Analysis (strengths and weaknesses)' },
        { value: 'creation', label: 'Creative Guidance (for new visual works)' }
      ],
      default: 'description',
      required: false
    },
    {
      id: 'contextualFactors',
      label: 'Contextual Factors',
      type: 'textarea',
      required: false,
      placeholder: 'Historical, cultural, or situational context relevant to understanding the visual element.'
    },
    {
      id: 'outputStyle',
      label: 'Output Style',
      type: 'select',
      options: [
        { value: 'systematic', label: 'Systematic Analysis (structured breakdown)' },
        { value: 'diagram', label: 'Diagrammatic (structured visual representation)' },
        { value: 'narrative', label: 'Narrative Description (flowing analytical text)' },
        { value: 'comparative', label: 'Comparative Analysis (relating to other visuals or concepts)' }
      ],
      default: 'systematic',
      required: false
    }
  ],
  reasoningModes: [
    'visual-decomposition',
    'chain-of-thought',
    'self-reflection',
    'hypothesis-driven',
    'prompt-synthesis'
  ],
  formatFnTemplate: `# Pentagram Visual Analysis System

## Subject for Analysis
{{scene}}

## Analysis Framework and Approach

{{#select analysisMode value="compositional"}}
### Compositional Elements Framework
I will analyze this visual subject through five key compositional elements:

1. **Form & Shape**: The structural elements, geometry, lines, and physical organization
2. **Color & Light**: The chromatic qualities, light interaction, contrast, and color relationships
3. **Space & Perspective**: The spatial organization, depth, dimensionality, and viewpoint
4. **Texture & Material**: The surface qualities, materiality, patterns, and tactile elements
5. **Movement & Rhythm**: The dynamic elements, suggested motion, flow, and visual rhythm
{{/select}}

{{#select analysisMode value="narrative"}}
### Narrative Components Framework
I will analyze this visual subject through five key narrative elements:

1. **Character & Subject**: The primary figures, subjects, or entities and their attributes
2. **Setting & Environment**: The context, location, time period, and environmental conditions
3. **Action & Event**: The activities, events, or implied narrative developments
4. **Symbolism & Metaphor**: The symbolic elements, metaphorical content, and cultural references
5. **Mood & Atmosphere**: The emotional tone, atmospheric qualities, and psychological impact
{{/select}}

{{#select analysisMode value="conceptual"}}
### Conceptual Mapping Framework
I will analyze this visual subject through five key conceptual dimensions:

1. **Core Concept**: The central idea, theme, or conceptual foundation
2. **Variations & Iterations**: The concept's variations, manifestations, or evolutionary forms
3. **Contextual Placement**: How the concept situates within broader frameworks or systems
4. **Implications & Extensions**: The concept's logical consequences and potential applications
5. **Tensions & Contradictions**: Internal conflicts, paradoxes, or oppositional elements
{{/select}}

{{#select analysisMode value="emotional"}}
### Emotional Impact Framework
I will analyze this visual subject through five key emotional dimensions:

1. **Primary Emotion**: The dominant emotional quality or affective response
2. **Emotional Intensity**: The strength, potency, or impact of the emotional content
3. **Emotional Contrast**: The juxtapositions, transitions, or contradictions in emotional tone
4. **Emotional Resonance**: The universal or culturally-specific emotional connections
5. **Emotional Subtext**: The underlying, implicit, or secondary emotional currents
{{/select}}

{{#select analysisMode value="technical"}}
### Technical Execution Framework
I will analyze this visual subject through five key technical dimensions:

1. **Medium & Materials**: The physical or digital substances and tools employed
2. **Technique & Method**: The procedural approaches and methodological choices
3. **Skill & Execution**: The technical proficiency and craftsmanship evident
4. **Innovation & Originality**: The novel, inventive, or groundbreaking technical aspects
5. **Constraints & Limitations**: The technical boundaries, challenges, or restrictions navigated
{{/select}}

{{#select purpose value="description"}}
### Descriptive Purpose
This analysis will focus on accurately describing and cataloging the visual elements present, with emphasis on objective observation rather than interpretation or judgment.
{{/select}}

{{#select purpose value="interpretation"}}
### Interpretive Purpose
This analysis will focus on uncovering meaning, significance, and communicative intent, with emphasis on what the visual elements might represent or symbolize.
{{/select}}

{{#select purpose value="evaluation"}}
### Evaluative Purpose
This analysis will focus on assessing strengths, weaknesses, effectiveness, and impact, with emphasis on how successfully the visual elements achieve their apparent aims.
{{/select}}

{{#select purpose value="creation"}}
### Creative Guidance Purpose
This analysis will focus on extracting principles, patterns, and insights that could guide the creation of new visual works, with emphasis on transferable techniques and approaches.
{{/select}}

{{#if contextualFactors}}
### Contextual Considerations
The following contextual factors will inform the analysis:
{{contextualFactors}}
{{/if}}

## Five-Point Analysis

{{#select outputStyle value="systematic"}}
I will present a systematic breakdown of each element in the pentagram framework, examining each in depth before synthesizing their interrelationships.
{{/select}}

{{#select outputStyle value="diagram"}}
I will present the analysis as a conceptual diagram with the five elements arranged in a pentagram structure, showing their relationships and interactions.
{{/select}}

{{#select outputStyle value="narrative"}}
I will present the analysis as a flowing analytical narrative that weaves together observations about all five elements into a cohesive discussion.
{{/select}}

{{#select outputStyle value="comparative"}}
I will present the analysis by comparing and contrasting the five elements with relevant precedents, alternatives, or contextual references.
{{/select}}

### Element 1: [First Pentagram Element]
[Detailed analysis of first element based on chosen framework]

### Element 2: [Second Pentagram Element]
[Detailed analysis of second element based on chosen framework]

### Element 3: [Third Pentagram Element]
[Detailed analysis of third element based on chosen framework]

### Element 4: [Fourth Pentagram Element]
[Detailed analysis of fourth element based on chosen framework]

### Element 5: [Fifth Pentagram Element]
[Detailed analysis of fifth element based on chosen framework]

## Element Integration and Relationships

### Interrelationships and Dynamics
[Analysis of how the five elements interact with and influence each other]

### Dominant and Subordinate Elements
[Discussion of the relative prominence and importance of each element]

### Synergies and Tensions
[Exploration of how elements work together or create productive tensions]

## Comprehensive Synthesis

### Holistic Interpretation
[Integration of all five elements into a unified understanding of the visual subject]

### Key Insights
[The most significant observations and revelations from the pentagram analysis]

### Reflection on the Analysis
[Meta-analysis of the effectiveness and limitations of this pentagram approach for this particular subject]`,
  outputFormat: 'markdown',
  constraints: {
    maxWords: 2000,
    disallowedTerms: ['pentagram framework', 'cannot be visualized']
  },
  examples: [
    {
      input: { 
        scene: 'A minimalist Japanese garden with raked gravel, carefully placed rocks, a small bamboo fountain, maple trees, and a stone path.',
        analysisMode: 'compositional',
        purpose: 'interpretation',
        contextualFactors: 'Traditional Japanese aesthetics emphasizing harmony, simplicity, and natural elements.',
        outputStyle: 'systematic'
      },
      output: '(Systematic compositional analysis of a Japanese garden examining form, color, space, texture, and movement through an interpretive lens informed by Japanese aesthetic traditions)'
    },
    {
      input: {
        scene: 'A concept for a futuristic sustainable smart city with vertical gardens, transparent solar panel buildings, automated transport pods, communal spaces, and water reclamation systems.',
        analysisMode: 'conceptual',
        purpose: 'creation',
        outputStyle: 'diagram'
      },
      output: '(Diagrammatic conceptual analysis of a smart city concept breaking down core concepts, variations, context, implications, and tensions to guide creative development)'
    }
  ]
};