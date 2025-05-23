import { AdvancedPromptTemplate } from '../types/promptTypes';

// export const deepResearchTemplate: AdvancedPromptTemplate = {
//   id: 'deep-research',
//   title: 'Deep Research',
//   description: 'Comprehensive research with evidence-based findings and citations',
//   version: '2.0',
//   icon: 'search',
//   color: '#4285F4', // Google blue
//   category: 'research',
//   parameters: [
//     {
//       id: 'topic',
//       label: 'Research Question',
//       type: 'textarea',
//       placeholder: 'What specific question needs to be researched?',
//       required: true
//     },
//     {
//       id: 'recency',
//       label: 'Recency Requirement',
//       type: 'select',
//       options: [
//         { value: '1', label: 'Last year only' },
//         { value: '3', label: 'Last 3 years' },
//         { value: '5', label: 'Last 5 years' },
//         { value: 'any', label: 'Any timeframe' }
//       ],
//       default: '3'
//     },
//     {
//       id: 'sourceTypes',
//       label: 'Preferred Source Types',
//       type: 'select',
//       options: [
//         { value: 'academic', label: 'Academic (studies, papers)' },
//         { value: 'government', label: 'Government sources' },
//         { value: 'news', label: 'News articles' },
//         { value: 'mixed', label: 'Mixed sources' }
//       ],
//       default: 'mixed'
//     },
//     {
//       id: 'format',
//       label: 'Output Format',
//       type: 'select',
//       options: [
//         { value: 'summary', label: 'Executive summary' },
//         { value: 'report', label: 'Detailed report' },
//         { value: 'comparative', label: 'Comparative analysis' }
//       ],
//       default: 'report'
//     }
//   ],
//   reasoningModes: [
//     'retrieval-augmented',
//     'chain-of-thought',
//     'self-reflection'
//   ],
//   formatFnTemplate: `### Deep Research Query

// ## Research Question
// {{topic}}

// ## Research Parameters
// {{#select recency value="1"}}
// - Recency requirement: Sources from within 1 year
// {{/select}}
// {{#select recency value="3"}}
// - Recency requirement: Sources from within 3 years
// {{/select}}
// {{#select recency value="5"}}
// - Recency requirement: Sources from within 5 years
// {{/select}}
// {{#select recency value="any"}}
// - Recency requirement: Sources from any relevant timeframe
// {{/select}}

// {{#select sourceTypes value="academic"}}
// - Source guidance: Prioritize academic sources (studies, peer-reviewed papers, institutional research)
// {{/select}}
// {{#select sourceTypes value="government"}}
// - Source guidance: Prioritize government and official sources (reports, statistics, policy documents)
// {{/select}}
// {{#select sourceTypes value="news"}}
// - Source guidance: Prioritize reputable news sources and industry publications
// {{/select}}
// {{#select sourceTypes value="mixed"}}
// - Source guidance: Use a mix of high-quality sources appropriate to the topic
// {{/select}}

// {{#select format value="summary"}}
// - Output format: Produce a concise executive summary with key findings and implications
// {{/select}}
// {{#select format value="report"}}
// - Output format: Create a comprehensive report with sections for methodology, findings, and conclusions
// {{/select}}
// {{#select format value="comparative"}}
// - Output format: Develop a comparative analysis that evaluates different perspectives or approaches
// {{/select}}

// ## Research Approach
// 1. Retrieve reliable sources relevant to the question
// 2. Extract key evidence and evaluate source credibility
// 3. Synthesize findings using Chain-of-Thought reasoning
// 4. Apply self-reflection to identify potential gaps or biases
// 5. Structure output according to specified format with proper citations

// ## Query Execution
// Conduct thorough research on this topic following the parameters above. For each significant claim, include a source citation. Organize findings according to the requested format, and conclude with a summary of key takeaways and any identified knowledge gaps.`,
//   outputFormat: 'markdown',
//   examples: [
//     {
//       input: {
//         topic: 'What are the environmental impacts of electric vehicles compared to conventional vehicles?',
//         recency: '3',
//         sourceTypes: 'academic',
//         format: 'comparative'
//       },
//       output: '(Example output with comparative analysis of EV environmental impacts)'
//     }
//   ]
// };
