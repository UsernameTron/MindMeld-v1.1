#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Get component and its new location
const component = process.argv[2];
const category = process.argv[3]; // atoms, molecules, organisms

if (!component || !category) {
  console.error('Usage: update-imports.js <ComponentName> <Category>');
  process.exit(1);
}

// Find all TypeScript/TSX files
const files = glob.sync('./frontend/src/**/*.{ts,tsx}', {
  ignore: ['**/node_modules/**', '**/dist/**'],
});

// Process each file
let updatedFiles = 0;
files.forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  // Look for imports of this component
  const importRegex = new RegExp(`import\\s+(.+)\\s+from\\s+['\"](.+/${component})['\"]`, 'g');
  let match;
  let newContent = content;
  let updated = false;
  while ((match = importRegex.exec(content)) !== null) {
    const importName = match[1];
    const oldPath = match[2];
    // The new import path
    const newPath = `@ui/${category}/${component}`;
    // Replace the import statement
    newContent = newContent.replace(
      `import ${importName} from '${oldPath}'`,
      `import ${importName} from '${newPath}'`,
    );
    updated = true;
  }
  // Write updated content back if changed
  if (updated) {
    fs.writeFileSync(file, newContent);
    updatedFiles++;
    console.log(`Updated imports in: ${file}`);
  }
});

console.log(`Updated imports in ${updatedFiles} files`);
