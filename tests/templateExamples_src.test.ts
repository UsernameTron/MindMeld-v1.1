import { AdvancedPromptTemplate } from '../types/promptTypes';

export const deepResearchTemplate: AdvancedPromptTemplate = {
  id: 'deep-research',
  title: 'Deep Research Protocol',
  description: 'Rigorous evidence-based research with comprehensive source evaluation, citation tracking, and structured synthesis',
  version: '2.0',
  icon: 'search',
  color: '#4285F4',
  category: 'research',
  parameters: [
    {
      id: 'topic',
      label: 'Research Question/Topic',
      type: 'textarea',
      placeholder: 'Specify your research question or topic with precision. More focused questions yield better results.',
      required: true
    },
    {
      id: 'recency',
      label: 'Temporal Scope',
      type: 'select',
      options: [
        { value: '1', label: 'Last year only (very recent developments)' },
        { value: '3', label: 'Last 3 years (current state of field)' },
        { value: '5', label: 'Last 5 years (medium-term developments)' },
        { value: '10', label: 'Last decade (broader historical context)' },
        { value: 'any', label: 'Any timeframe (including historical perspective)' }
      ],
      default: '3',
      required: true
    },
    {
      id: 'sourceTypes',
      label: 'Source Hierarchy',
      type: 'select',
      options: [
        { value: 'academic', label: 'Academic (peer-reviewed studies, institutional research)' },
        { value: 'government', label: 'Government/Official (policy documents, statistics)' },
        { value: 'industry', label: 'Industry Reports (market analysis, white papers)' },
        { value: 'news', label: 'News/Journalism (event reporting, analysis)' },
        { value: 'mixed', label: 'Mixed sources (balanced approach)' }
      ],
      default: 'mixed',
      required: true
    },
    {
      id: 'depth',
      label: 'Research Depth',
      type: 'select',
      options: [
        { value: 'survey', label: 'Survey (broad overview of key points)' },
        { value: 'standard', label: 'Standard (balanced depth and breadth)' },
        { value: 'comprehensive', label: 'Comprehensive (detailed analysis)' },
        { value: 'exhaustive', label: 'Exhaustive (maximum possible detail)' }
      ],
      default: 'standard',
      required: false
    },
    {
      id: 'perspectiveBalance',
      label: 'Perspective Balance',
      type: 'select',
      options: [
        { value: 'consensus', label: 'Consensus View (mainstream positions)' },
        { value: 'balanced', label: 'Balanced (equal treatment of competing views)' },
        { value: 'contrarian', label: 'Contrarian Focus (emphasis on alternative views)' },
        { value: 'comprehensive', label: 'Comprehensive (all significant perspectives)' }
      ],
      default: 'balanced',
      required: false
    },
    {
      id: 'citationStyle',
      label: 'Citation Style',
      type: 'select',
      options: [
        { value: 'APA', label: 'APA Style' },
        { value: 'MLA', label: 'MLA Style' },
        { value: 'Chicago', label: 'Chicago Style' },
        { value: 'IEEE', label: 'IEEE Style' },
        { value: 'Harvard', label: 'Harvard Style' }
      ],
      default: 'APA',
      required: false
    },
    {
      id: 'format',
      label: 'Output Format',
      type: 'select',
      options: [
        { value: 'summary', label: 'Executive Summary (concise overview)' },
        { value: 'report', label: 'Formal Report (structured, comprehensive)' },
        { value: 'comparative', label: 'Comparative Analysis (contrasting views)' },
        { value: 'annotated', label: 'Annotated Bibliography (source-focused)' },
        { value: 'literature', label: 'Literature Review (research synthesis)' }
      ],
      default: 'report',
      required: true
    }
  ],
  reasoningModes: [
    'retrieval-augmented',
    'source-anchors',
    'evidence-ranking',
    'chain-of-thought',
    'adversarial-fact-check',
    'self-reflection'
  ],
  formatFnTemplate: `# Deep Research Protocol

## Research Question/Topic
{{topic}}

## Research Parameters

### Temporal Scope
{{#select recency value="1"}}
- Temporal focus: Last year only (very recent developments)
- Source recency requirement: Sources published within the past 12 months will be prioritized
- Historical context: Minimal, focused on immediate developments
{{/select}}
{{#select recency value="3"}}
- Temporal focus: Last 3 years (current state of field)
- Source recency requirement: Primarily sources from within the past 3 years
- Historical context: Brief background from earlier periods when necessary
{{/select}}
{{#select recency value="5"}}
- Temporal focus: Last 5 years (medium-term developments)
- Source recency requirement: Emphasis on sources from within the past 5 years
- Historical context: Moderate historical context to situate current developments
{{/select}}
{{#select recency value="10"}}
- Temporal focus: Last decade (broader historical context)
- Source recency requirement: Balance of recent and older sources spanning the past decade
- Historical context: Substantial attention to evolving trends and developments
{{/select}}
{{#select recency value="any"}}
- Temporal focus: Any timeframe (including historical perspective)
- Source recency requirement: Sources selected based on relevance rather than recency
- Historical context: Comprehensive historical perspective integrated throughout
{{/select}}

### Source Hierarchy and Evaluation
{{#select sourceTypes value="academic"}}
- **Primary source types**: Peer-reviewed journal articles, conference proceedings, academic books
- **Secondary source types**: University publications, educational resources, academic lectures
- **Source evaluation criteria**: Peer-review status, citation count, author expertise, institutional affiliation
- **Credibility threshold**: High - emphasizing methodologically sound studies from reputable institutions
{{/select}}
{{#select sourceTypes value="government"}}
- **Primary source types**: Official reports, statistics, policy documents, legislative records
- **Secondary source types**: Government-funded research, public statements, regulatory guidelines
- **Source evaluation criteria**: Authority level, data collection methodology, recency, objectivity
- **Credibility threshold**: Official sources with transparent methodologies
{{/select}}
{{#select sourceTypes value="industry"}}
- **Primary source types**: Industry reports, white papers, market analyses, technical documentation
- **Secondary source types**: Trade publications, company research, product specifications
- **Source evaluation criteria**: Methodological transparency, author expertise, company reputation, disclosure of conflicts
- **Credibility threshold**: Reports with transparent methodologies and limited commercial bias
{{/select}}
{{#select sourceTypes value="news"}}
- **Primary source types**: Investigative journalism, analysis from major outlets, expert interviews
- **Secondary source types**: News reports, press releases, journalistic summaries
- **Source evaluation criteria**: Publication reputation, journalist expertise, corroboration, transparency
- **Credibility threshold**: Reporting from established outlets with fact-checking processes
{{/select}}
{{#select sourceTypes value="mixed"}}
- **Primary source types**: Balanced mix of academic, governmental, industry, and journalistic sources
- **Secondary source types**: Various supplementary sources appropriate to the topic
- **Source evaluation criteria**: Adapted to each source type while maintaining consistent quality standards
- **Credibility threshold**: Appropriate to source type, with preference for higher-quality sources
{{/select}}

### Research Depth
{{#select depth value="survey"}}
- **Depth level**: Survey (broad overview)
- **Scope**: Covering major points and key developments
- **Detail level**: Moderate detail on core concepts, minimal detail on peripheral aspects
- **Examples**: Few, selected for representativeness
{{/select}}
{{#select depth value="standard"}}
- **Depth level**: Standard (balanced depth and breadth)
- **Scope**: Thorough coverage of main aspects, acknowledgment of secondary aspects
- **Detail level**: Substantial detail on core concepts, moderate detail on important secondary aspects
- **Examples**: Multiple, illustrating key points
{{/select}}
{{#select depth value="comprehensive"}}
- **Depth level**: Comprehensive (detailed analysis)
- **Scope**: Extensive coverage of primary and secondary aspects
- **Detail level**: Extensive detail throughout, with particular depth on complex or contested areas
- **Examples**: Numerous, covering various facets and edge cases
{{/select}}
{{#select depth value="exhaustive"}}
- **Depth level**: Exhaustive (maximum possible detail)
- **Scope**: All significant aspects covered with attention to nuance and complexity
- **Detail level**: Maximum detail throughout, including technical specifics and theoretical foundations
- **Examples**: Comprehensive range, systematically addressing the full spectrum of cases
{{/select}}

### Perspective Balance
{{#select perspectiveBalance value="consensus"}}
- **Perspective approach**: Consensus View (mainstream positions)
- **Weight distribution**: Primary emphasis on widely accepted positions
- **Alternative view handling**: Noted but not emphasized
- **Controversy treatment**: Acknowledgment with focus on points of agreement
{{/select}}
{{#select perspectiveBalance value="balanced"}}
- **Perspective approach**: Balanced (equal treatment of competing views)
- **Weight distribution**: Proportional representation of major positions
- **Alternative view handling**: Presented alongside mainstream views
- **Controversy treatment**: Detailed exploration of points of contention
{{/select}}
{{#select perspectiveBalance value="contrarian"}}
- **Perspective approach**: Contrarian Focus (emphasis on alternative views)
- **Weight distribution**: Greater emphasis on under-represented or challenging positions
- **Alternative view handling**: Prominent featuring with critical analysis
- **Controversy treatment**: Centered on challenging conventional wisdom
{{/select}}
{{#select perspectiveBalance value="comprehensive"}}
- **Perspective approach**: Comprehensive (all significant perspectives)
- **Weight distribution**: Coverage proportional to significance in the field
- **Alternative view handling**: Thorough treatment of all substantial positions
- **Controversy treatment**: Systematic analysis of all major debates
{{/select}}

## Research Methodology

### Source Retrieval and Evaluation Protocol
1. **Initial source gathering**: Identify and collect relevant sources according to the specified parameters
2. **Source classification**: Categorize sources by type, recency, and relevance
3. **Source evaluation**: Apply appropriate credibility criteria based on source type
4. **Source ranking**: Prioritize sources based on authority, relevance, and quality
5. **Evidence extraction**: Systematically extract key claims, data, and arguments
6. **Claim verification**: Cross-check significant claims across multiple sources when possible
7. **Source mapping**: Identify relationships, agreements, and contradictions between sources

### Analytical Framework
1. **Knowledge synthesis**: Integrate information across sources using chain-of-thought reasoning
2. **Gap identification**: Identify areas of incomplete or conflicting information
3. **Perspective analysis**: Compare different viewpoints using specified perspective balance
4. **Critical evaluation**: Apply adversarial fact-checking to test strongest claims
5. **Self-reflection**: Assess potential bias in source selection or interpretation
6. **Confidence assessment**: Evaluate certainty levels for key conclusions based on evidence quality

## Output Structure

{{#select format value="summary"}}
### Executive Summary Format
I will produce a concise executive summary with:
- Brief introduction establishing context
- Key findings presented in order of significance
- Implications and applications of findings
- Areas requiring further research
- Highly synthesized conclusions
{{/select}}

{{#select format value="report"}}
### Formal Report Format
I will create a comprehensive report with:
1. **Executive Summary**: Brief overview of key findings
2. **Introduction**: Context, scope, and significance
3. **Methodology**: Research approach and source evaluation
4. **Findings**: Systematic presentation of research results
5. **Analysis**: Interpretation and synthesis of findings
6. **Discussion**: Implications, applications, and limitations
7. **Conclusion**: Summary of key insights and significance
8. **References**: Complete source list in {{citationStyle}} format
{{/select}}

{{#select format value="comparative"}}
### Comparative Analysis Format
I will develop a comparative analysis with:
1. **Framework**: Establish analytical categories and criteria
2. **Position Mapping**: Systematically outline major perspectives
3. **Comparative Evaluation**: Direct comparison across established criteria
4. **Strengths/Weaknesses**: Analysis of each major position
5. **Synthesis**: Identification of commonalities and irreconcilable differences
6. **Implications**: Practical or theoretical significance of the comparison
7. **References**: Complete source list in {{citationStyle}} format
{{/select}}

{{#select format value="annotated"}}
### Annotated Bibliography Format
I will create an annotated bibliography with:
1. **Introduction**: Brief overview of the research area and sources
2. **Source Entries**: Each significant source with:
   - Complete citation in {{citationStyle}} format
   - Summary of key content and arguments
   - Evaluation of credibility and significance
   - Relevance to the research question
3. **Synthesis**: Overall patterns and insights across sources
4. **Research Gaps**: Identification of areas needing further investigation
{{/select}}

{{#select format value="literature"}}
### Literature Review Format
I will produce a literature review with:
1. **Introduction**: Scope, purpose, and organization of the review
2. **Theoretical Framework**: Key concepts and their relationships
3. **Historical Development**: Evolution of research on the topic
4. **Current State of Knowledge**: Organized by themes or approaches
5. **Controversies and Debates**: Analysis of contested areas
6. **Research Gaps**: Identification of understudied aspects
7. **Future Directions**: Promising avenues for further research
8. **References**: Complete source list in {{citationStyle}} format
{{/select}}

## Citation Protocol
- **Citation style**: {{citationStyle}}
- **In-text citation format**: Following {{citationStyle}} guidelines
- **Citation frequency**: Every substantive claim will be cited
- **Multiple source handling**: Synthesis of information across sources will be indicated
- **Bibliography organization**: Alphabetical by author surname per {{citationStyle}} rules

## Research Execution
I will now conduct thorough research on this topic following the parameters above. For each significant claim, I will include a source citation. I will organize findings according to the requested format, and conclude with a summary of key takeaways and identified knowledge gaps.`,
  outputFormat: 'markdown',
  constraints: {
    sourceRecency: 10,
    citationStyle: 'APA',
    sourceCredibilityTier: 'academic',
    minWords: 500,
    maxWords: 5000,
    requiredTerms: ['sources', 'research', 'evidence']
  },
  outputVerification: {
    requiresCitations: true,
    confidenceThreshold: 80,
    validateStructure: true
  },
  examples: [
    {
      input: {
        topic: 'What are the environmental impacts of electric vehicles compared to conventional vehicles, considering full lifecycle analysis?',
        recency: '3',
        sourceTypes: 'academic',
        depth: 'comprehensive',
        perspectiveBalance: 'balanced',
        format: 'comparative',
        citationStyle: 'APA'
      },
      output: '(Comprehensive comparative analysis of EV environmental impacts using lifecycle assessment methodology, balanced treatment of benefits and limitations)'
    },
    {
      input: {
        topic: 'How has remote work affected productivity, employee wellbeing, and corporate culture since 2020?',
        recency: '1',
        sourceTypes: 'mixed',
        depth: 'standard',
        perspectiveBalance: 'comprehensive',
        format: 'report',
        citationStyle: 'Chicago'
      },
      output: '(Formal report on remote work impacts with mixed sources, addressing productivity metrics, psychological effects, and organizational changes)'
    }
  ]
};
