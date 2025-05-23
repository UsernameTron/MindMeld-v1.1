import { AdvancedPromptTemplate } from '../../types/promptTypes';

export const satiricalVoiceTemplate: AdvancedPromptTemplate = {
  id: 'satirical-voice',
  title: 'Satirical Voice Transformation System',
  description: 'Transform content into sophisticated satirical compositions with calibrated tone, targeted critique, and strategic comedic techniques',
  version: '2.0',
  icon: 'sentiment_very_satisfied',
  color: '#FBC02D',
  category: 'tone-transformation',
  parameters: [
    {
      id: 'content',
      label: 'Original Content',
      type: 'textarea',
      required: true,
      placeholder: 'Enter the text or describe the topic you want to transform with satirical treatment.'
    },
    {
      id: 'target',
      label: 'Satirical Target',
      type: 'select',
      options: [
        { value: 'corporate', label: 'Corporate Culture & Bureaucracy' },
        { value: 'tech', label: 'Technology & Innovation Hype' },
        { value: 'politics', label: 'Political Rhetoric & Posturing' },
        { value: 'academia', label: 'Academic Pretension & Jargon' },
        { value: 'consumer', label: 'Consumer Trends & Marketing' },
        { value: 'self-help', label: 'Self-Improvement Culture' },
        { value: 'media', label: 'Media & Entertainment Conventions' }
      ],
      default: 'corporate',
      required: true
    },
    {
      id: 'satireModes',
      label: 'Satire Intensity & Approach',
      type: 'select',
      options: [
        { value: 'high-satire', label: 'High Satire (maximum bite, sophisticated irony)' },
        { value: 'strategic-snark', label: 'Strategic Snark (pointed but constructive)' },
        { value: 'soft-roast', label: 'Soft Roast (gentle, accessible humor)' },
        { value: 'deadpan', label: 'Deadpan Absurdism (straight-faced extremity)' },
        { value: 'socratic', label: 'Socratic Irony (feigned ignorance)' }
      ],
      default: 'strategic-snark',
      required: true
    },
    {
      id: 'techniques',
      label: 'Primary Satirical Techniques',
      type: 'select',
      options: [
        { value: 'exaggeration', label: 'Hyperbole & Exaggeration' },
        { value: 'ironic-reversal', label: 'Ironic Reversal' },
        { value: 'parody', label: 'Parody & Imitation' },
        { value: 'reduction', label: 'Reductio ad Absurdum' },
        { value: 'juxtaposition', label: 'Incongruous Juxtaposition' },
        { value: 'euphemism', label: 'Satirical Euphemism & Understatement' }
      ],
      default: 'exaggeration',
      required: false
    },
    {
      id: 'voiceStyle',
      label: 'Voice & Style',
      type: 'select',
      options: [
        { value: 'eloquent', label: 'Eloquent Sophisticate (elevated, verbose)' },
        { value: 'caustic', label: 'Caustic Observer (sharp, incisive)' },
        { value: 'folksy', label: 'Folksy Truth-teller (accessible, colloquial)' },
        { value: 'analytical', label: 'Pseudo-Analytical (mock-academic)' },
        { value: 'insider', label: 'Jaded Insider (knowing, world-weary)' }
      ],
      default: 'caustic',
      required: false
    },
    {
      id: 'outputFormat',
      label: 'Output Format',
      type: 'select',
      options: [
        { value: 'essay', label: 'Satirical Essay/Commentary' },
        { value: 'news', label: 'Satirical News Article' },
        { value: 'review', label: 'Satirical Review/Critique' },
        { value: 'guide', label: 'Satirical Guide/Manual' },
        { value: 'dialogue', label: 'Satirical Dialogue/Interview' },
        { value: 'social', label: 'Social Media Content' }
      ],
      default: 'essay',
      required: true
    }
  ],
  reasoningModes: [
    'adversarial-critique',
    'self-reflection',
    'chain-of-thought'
  ],
  toneMode: 'high-satire',
  formatFnTemplate: `# Satirical Voice Transformation System

## Original Content/Subject
{{content}}

## Satirical Parameters

### Target Domain
{{#select target value="corporate"}}
**Corporate Culture & Bureaucracy**
- Target elements: Management speak, organizational rituals, hierarchy worship, efficiency theater, performative professionalism
- Cultural references: Office Space, Dilbert, corporate mission statements, team-building exercises, synergy buzzwords
- Core absurdities: Elaborate procedures that impede actual work, reverence for incompetent leadership, euphemistic language for negative actions
{{/select}}

{{#select target value="tech"}}
**Technology & Innovation Hype**
- Target elements: Techno-utopianism, disruption rhetoric, funding cycles, innovation theater, tech messiah figures
- Cultural references: Silicon Valley, TED Talks, pitch decks, venture capital, "world-changing" apps that solve trivial problems
- Core absurdities: Trivial conveniences presented as revolutionary, technical solutions for social problems, funding divorced from utility
{{/select}}

{{#select target value="politics"}}
**Political Rhetoric & Posturing**
- Target elements: Empty campaign promises, tribalism, performative outrage, linguistic manipulation, symbolic gestures
- Cultural references: Political speeches, cable news, party platforms, meaningless slogans, partisan media
- Core absurdities: Words contradicting actions, manufactured crises, treating politics as team sports, policy vs. presentation
{{/select}}

{{#select target value="academia"}}
**Academic Pretension & Jargon**
- Target elements: Impenetrable jargon, publication politics, intellectual fashions, citation games, disciplinary turf wars
- Cultural references: Academic journals, conference presentations, peer review, theory-laden abstracts, funding proposals
- Core absurdities: Simple ideas hidden behind complex language, status games disguised as intellectual pursuit, knowing more and more about less and less
{{/select}}

{{#select target value="consumer"}}
**Consumer Trends & Marketing**
- Target elements: Aspirational branding, artificial needs, status signaling, commodity fetishism, lifestyle marketing
- Cultural references: Luxury advertising, influencer culture, unboxing videos, lifestyle brands, product launches
- Core absurdities: Identity via consumption, engineered dissatisfaction, minimal differentiation presented as revolutionary, price as quality proxy
{{/select}}

{{#select target value="self-help"}}
**Self-Improvement Culture**
- Target elements: Quick-fix promises, contradictory advice, productivity worship, authenticity as performance, life optimization
- Cultural references: Self-help bestsellers, motivational speakers, productivity systems, life hacks, morning routines
- Core absurdities: Commodification of wisdom, quantification of human experience, pursuing happiness as productivity, success theater
{{/select}}

{{#select target value="media"}}
**Media & Entertainment Conventions**
- Target elements: Clickbait, formulaic content, manufactured controversy, spectacle economics, attention harvesting
- Cultural references: Headline conventions, reality TV, social media algorithms, content farms, engagement metrics
- Core absurdities: Medium over message, emotional manipulation as business model, predictability marketed as novelty
{{/select}}

### Satire Intensity & Approach

{{#select satireModes value="high-satire"}}
**High Satire Mode**
- Tone calibration: Maximum bite with intellectual sophistication
- Emotional register: Cold, merciless dissection with elegant contempt
- Humor approach: Elaborate irony requiring high context awareness
- Restraint level: Minimal - full satirical force deployed
- Language level: Elevated, possibly archaic or formal diction

*Exemplars: Jonathan Swift, Gore Vidal, Christopher Hitchens*
{{/select}}

{{#select satireModes value="strategic-snark"}}
**Strategic Snark Mode**
- Tone calibration: Sharp critique balanced with constructive insight
- Emotional register: Knowing frustration with path toward improvement
- Humor approach: Pointed observations that recognize absurdity while suggesting alternatives
- Restraint level: Moderate - criticism channeled toward productive ends
- Language level: Accessible but intelligent, avoiding excessive jargon

*Exemplars: Jon Stewart, John Oliver, Rebecca Solnit*
{{/select}}

{{#select satireModes value="soft-roast"}}
**Soft Roast Mode**
- Tone calibration: Gentle ribbing with underlying affection
- Emotional register: Warm amusement rather than bitter critique
- Humor approach: Accessible comedy that invites subject into the joke
- Restraint level: High - criticism softened with goodwill
- Language level: Conversational, widely accessible

*Exemplars: Ellen DeGeneres, Jim Gaffigan, Nora Ephron*
{{/select}}

{{#select satireModes value="deadpan"}}
**Deadpan Absurdism Mode**
- Tone calibration: Completely straight-faced presentation of absurdity
- Emotional register: Flat affect contrasting with ridiculous content
- Humor approach: Extreme logic taken to absurd conclusions without acknowledging the joke
- Restraint level: Paradoxical - extreme content with extremely controlled delivery
- Language level: Matter-of-fact, often technical or bureaucratic

*Exemplars: The Onion, Steven Wright, Wes Anderson*
{{/select}}

{{#select satireModes value="socratic"}}
**Socratic Irony Mode**
- Tone calibration: Feigned ignorance or naivety to expose absurdity
- Emotional register: False innocence masking deeper understanding
- Humor approach: Questions and "misunderstandings" that reveal contradictions
- Restraint level: High - critique disguised as genuine inquiry
- Language level: Simple questions hiding complex critique

*Exemplars: Stephen Colbert (character), Borat, Some Andy Kaufman*
{{/select}}

### Primary Satirical Techniques

{{#select techniques value="exaggeration"}}
**Hyperbole & Exaggeration**
- Take actual elements and magnify them to reveal their absurdity
- Push logical conclusions to extreme endpoints
- Employ comedic overkill to highlight proportionality problems
{{/select}}

{{#select techniques value="ironic-reversal"}}
**Ironic Reversal**
- Present the opposite of expected positions or outcomes
- Utilize contrapuntal logic and inversion of normal values
- Subvert expectations through reversed cause-effect relationships
{{/select}}

{{#select techniques value="parody"}}
**Parody & Imitation**
- Mimic the style, structure, and conventions of the target
- Exaggerate characteristic elements while maintaining recognizability
- Create funhouse mirror reflections that reveal underlying patterns
{{/select}}

{{#select techniques value="reduction"}}
**Reductio ad Absurdum**
- Follow the internal logic of ideas to ridiculous conclusions
- Strip away justifications to expose underlying contradictions
- Simplify complex rationalizations to reveal basic fallacies
{{/select}}

{{#select techniques value="juxtaposition"}}
**Incongruous Juxtaposition**
- Place unrelated elements in unexpected proximity
- Create cognitive dissonance through contextual shifts
- Highlight contradictions by forcing incompatible ideas together
{{/select}}

{{#select techniques value="euphemism"}}
**Satirical Euphemism & Understatement**
- Use deliberately mild language for extreme situations
- Employ corporate or bureaucratic language for human experiences
- Create comedic tension through inappropriately moderate descriptions
{{/select}}

### Voice & Stylistic Approach

{{#select voiceStyle value="eloquent"}}
**Eloquent Sophisticate**
- Voice characteristics: Verbose, elevated diction, elaborate sentence structures
- Stylistic elements: Literary allusions, ornate metaphors, archaic phrasings
- Comedic contrast: High language applied to low subjects
{{/select}}

{{#select voiceStyle value="caustic"}}
**Caustic Observer**
- Voice characteristics: Sharp, incisive, economical, unsparing
- Stylistic elements: Cutting observations, surgical precision, memorable zingers
- Comedic contrast: No-nonsense clarity exposing euphemistic nonsense
{{/select}}

{{#select voiceStyle value="folksy"}}
**Folksy Truth-teller**
- Voice characteristics: Colloquial, accessible, seemingly simple
- Stylistic elements: Metaphors drawn from everyday life, commonsense observations
- Comedic contrast: Homespun wisdom undermining pretentious complexity
{{/select}}

{{#select voiceStyle value="analytical"}}
**Pseudo-Analytical**
- Voice characteristics: Mock-academic, data-focused, systematizing
- Stylistic elements: Faux research, taxonomies of absurdity, quantification of the unquantifiable
- Comedic contrast: Scientific rigor applied to fundamentally unscientific subjects
{{/select}}

{{#select voiceStyle value="insider"}}
**Jaded Insider**
- Voice characteristics: World-weary, knowing, slightly conspiratorial
- Stylistic elements: Behind-the-scenes revelations, cynical asides, insider jargon
- Comedic contrast: The gap between public presentation and private reality
{{/select}}

### Output Format Structure

{{#select outputFormat value="essay"}}
**Satirical Essay/Commentary Format**
- Structure: Introduction establishing satirical premise, development through examples and arguments, crescendo to conclusion
- Voice positioning: Authoritative cultural commentator
- Length calibration: Extended development of satirical thesis
{{/select}}

{{#select outputFormat value="news"}}
**Satirical News Article Format**
- Structure: Headline, lede paragraph, quotes from fictional sources, background context
- Voice positioning: Ostensibly objective journalist
- Length calibration: Inverted pyramid structure with most absurd elements front-loaded
{{/select}}

{{#select outputFormat value="review"}}
**Satirical Review/Critique Format**
- Structure: Overview, criteria establishment, point-by-point assessment, final rating/recommendation
- Voice positioning: Discerning critic with implied expertise
- Length calibration: Balanced assessment with emphasis on evaluative language
{{/select}}

{{#select outputFormat value="guide"}}
**Satirical Guide/Manual Format**
- Structure: Introduction to subject, step-by-step instructions, troubleshooting section, expected results
- Voice positioning: Authoritative expert providing practical direction
- Length calibration: Procedural breakdown with satirical asides
{{/select}}

{{#select outputFormat value="dialogue"}}
**Satirical Dialogue/Interview Format**
- Structure: Introduction of participants, question-answer format, concluding exchange
- Voice positioning: Interviewer and subject with contrasting perspectives
- Length calibration: Exchange that builds in satirical intensity
{{/select}}

{{#select outputFormat value="social"}}
**Social Media Content Format**
- Structure: Platform-appropriate formatting, brevity, punchline focus
- Voice positioning: Viral-optimized cultural commentator
- Length calibration: Short-form with maximum impact in minimal space
{{/select}}

## Satirical Style Guidelines

### Core Principles
- Punch up, never down (target power, not vulnerability)
- Every satirical point should have an underlying serious purpose
- Maintain plausible deniability through sufficient exaggeration
- Use specificity rather than generality for sharper impact
- Employ contrast between style and substance for comedic effect

### Structural Techniques
- Use short paragraphs (3 lines maximum) for punchier delivery
- Start strong with a provocative or surprising opening
- End with a powerful final thought or punchline
- Incorporate occasional callbacks to earlier satirical elements
- Maintain a rhythm of setup and payoff throughout

### Language Approach
- Exploit the gap between language and reality
- Use the target's own terminology against itself
- Employ strategic shifts between high and low diction
- Create memorable satirical coinages or definitions
- Leverage syntactic patterns for comedic effect

## Satirical Transformation Execution
I'll now transform the content using the specified parameters, maintaining the appropriate satirical mode while delivering maximum comedic and critical impact.`,
  outputFormat: 'markdown',
  constraints: {
    maxWords: 1500,
    disallowedTerms: [
      'satire profile',
      'joke mechanism',
      'humor algorithm',
      'offensive language',
      'discriminatory content'
    ]
  },
  styleMandatory: [
    'Concrete specificity',
    'Punching up not down',
    'Rhythmic pacing',
    'Strong opening and closing',
    'Targeted precision'
  ],
  styleForbidden: [
    'Explaining the joke',
    'Apologizing for critique',
    'Padding with fluff',
    'Punching down',
    'Meandering digressions'
  ],
  behaviorSwitches: [
    'high-satire',
    'strategic-snark',
    'soft-roast',
    'deadpan',
    'socratic'
  ],
  examples: [
    {
      input: {
        content: 'Corporate wellness programs that encourage employees to track their steps, meditation minutes, and sleep quality while working 60-hour weeks',
        target: 'corporate',
        satireModes: 'high-satire',
        techniques: 'ironic-reversal',
        voiceStyle: 'caustic',
        outputFormat: 'essay'
      },
      output: '(Caustic satirical essay on corporate wellness programs that highlights the irony of monitoring employee health while ignoring structural workplace issues)'
    },
    {
      input: {
        content: 'The latest AI tool that promises to revolutionize creativity by generating content based on prompts',
        target: 'tech',
        satireModes: 'strategic-snark',
        techniques: 'reduction',
        voiceStyle: 'insider',
        outputFormat: 'review'
      },
      output: '(Strategic-snark review from an insider perspective on AI creativity tools, reducing the hyperbolic claims to their logical absurdities while acknowledging genuine potential)'
    }
  ]
};
