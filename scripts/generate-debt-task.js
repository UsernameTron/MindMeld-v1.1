#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const componentName = process.argv[2];
if (!componentName) {
  console.error('Usage: generate-debt-task.js <ComponentName>');
  process.exit(1);
}

const template = fs.readFileSync('./docs/technical-debt/reduction-template.md', 'utf8');
const taskContent = template.replace(/\[ComponentName\]/g, componentName);

const outputPath = `./docs/technical-debt/${componentName.toLowerCase()}-debt-reduction.md`;
fs.writeFileSync(outputPath, taskContent);
console.log(`Task created at: ${outputPath}`);
