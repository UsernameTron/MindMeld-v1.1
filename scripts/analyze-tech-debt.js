#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Analyze component structure
const componentDirs = fs.readdirSync('./frontend/src/components')
  .filter(dir => fs.statSync(`./frontend/src/components/${dir}`).isDirectory());

console.log('# Technical Debt Analysis Report\n');

// Check for inconsistent directory structures
console.log('## Component Structure Issues\n');
const nestedDirs = ['atoms', 'molecules', 'organisms', 'ui'];
const nestedComponents = [];
nestedDirs.forEach(nested => {
  const nestedPath = `./frontend/src/components/${nested}`;
  if (fs.existsSync(nestedPath) && fs.statSync(nestedPath).isDirectory()) {
    const comps = fs.readdirSync(nestedPath)
      .filter(dir => fs.statSync(`${nestedPath}/${dir}`).isDirectory());
    nestedComponents.push(...comps.map(c => `${nested}/${c}`));
  }
});

console.log(`- ${componentDirs.length} top-level components found`);
console.log(`- ${nestedComponents.length} nested components found`);
console.log('- Components found in multiple locations:');
const allNames = [...componentDirs, ...nestedComponents.map(c => c.split('/')[1])];
const duplicates = allNames.filter((name, index) => allNames.indexOf(name) !== index);
duplicates.forEach(dup => console.log(`  - ${dup}`));

// Check for missing tests
console.log('\n## Testing Gaps\n');
const missingTests = [];
componentDirs.forEach(dir => {
  const testPath = `./frontend/src/components/${dir}/${dir}.test.tsx`;
  if (!fs.existsSync(testPath)) {
    missingTests.push(dir);
  }
});
console.log(`- ${missingTests.length} components without tests:`);
missingTests.forEach(comp => console.log(`  - ${comp}`));

// Check for missing Storybook stories
console.log('\n## Documentation Issues\n');
const missingStories = [];
componentDirs.forEach(dir => {
  const storyPath = `./frontend/src/components/${dir}/${dir}.stories.tsx`;
  if (!fs.existsSync(storyPath)) {
    missingStories.push(dir);
  }
});
console.log(`- ${missingStories.length} components without Storybook stories:`);
missingStories.forEach(comp => console.log(`  - ${comp}`));

// Create prioritized list
console.log('\n## Prioritized Technical Debt Items\n');
console.log('1. Consolidate duplicate component implementations');
console.log('2. Add missing tests for components');
console.log('3. Add missing Storybook documentation');
console.log('4. Standardize component directory structure');
console.log('5. Update imports to use path aliases');
