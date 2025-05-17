const fs = require('fs');
const path = require('path');

// Expected components from project board
const components = [
  { name: 'Button', sprint: 'Sprint 2', category: 'atom' },
  { name: 'Card', sprint: 'Sprint 2', category: 'molecule' },
  { name: 'Select', sprint: 'Sprint 2', category: 'atom' },
  { name: 'LoadingIndicator', sprint: 'Sprint 2', category: 'molecule' },
  { name: 'ErrorDisplay', sprint: 'Sprint 2', category: 'molecule' },
  { name: 'FeatureErrorBoundary', sprint: 'Sprint 2', category: 'organism' },
  { name: 'CodeEditor', sprint: 'Sprint 3', category: 'organism' },
  { name: 'AnalysisResult', sprint: 'Sprint 3', category: 'organism' },
];

// Implementation status
const results = components.map(component => {
  // Try multiple possible locations
  const possiblePaths = [
    `./frontend/src/components/${component.name}`,
    `./frontend/src/components/ui/${component.category}s/${component.name}`,
    `./frontend/src/components/ui/${component.name}`,
    `./frontend/src/components/${component.category}s/${component.name}`,
  ];
  
  let componentPath = null;
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      componentPath = p;
      break;
    }
  }
  
  const implemented = !!componentPath;
  const tested = implemented && fs.existsSync(path.join(componentPath, `${component.name}.test.tsx`));
  const documented = implemented && fs.existsSync(path.join(componentPath, `${component.name}.stories.tsx`));
  
  return {
    ...component,
    implemented,
    tested,
    documented,
    status: implemented && tested && documented ? 'Complete' : 
           implemented ? 'Partial' : 'Not Implemented',
  };
});

// Create markdown report
const report = `# MindMeld Implementation Status Report\n\n## Component Status\n\n| Component | Sprint | Status | Implementation | Tests | Documentation |\n|-----------|--------|--------|----------------|-------|---------------|\n${
  results.map(r => `| ${r.name} | ${r.sprint} | ${r.status} | ${r.implemented ? '✅' : '❌'} | ${r.tested ? '✅' : '❌'} | ${r.documented ? '✅' : '❌'} |`).join('\n')
}\n`;

fs.writeFileSync('IMPLEMENTATION_STATUS.md', report);
console.log('Implementation status report generated');
