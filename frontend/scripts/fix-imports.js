const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find all TypeScript files
const files = glob.sync('src/**/*.{ts,tsx}', { cwd: process.cwd() });

// Extensions to check
const extensions = ['.ts', '.tsx', '.js', '.jsx'];

console.log(`Found ${files.length} files to process`);

let totalFixed = 0;
files.forEach(file => {
  const filePath = path.resolve(process.cwd(), file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Match import statements with relative paths
  const importRegex = /from\s+['"](\.[^'"]+)['"]/g;
  let match;
  let modified = false;
  let fixCount = 0;
  
  // Reset regex lastIndex
  importRegex.lastIndex = 0;
  
  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1];
    
    // Skip if already has extension
    if (path.extname(importPath)) continue;
    
    // Check if file exists with various extensions
    for (const ext of extensions) {
      const importDir = path.dirname(filePath);
      const fullPath = path.resolve(importDir, `${importPath}${ext}`);
      
      try {
        if (fs.existsSync(fullPath)) {
          // Replace import path with extension
          const newImport = `from '${importPath}${ext}'`;
          const oldImport = `from '${importPath}'`;
          
          if (content.includes(oldImport)) {
            content = content.replace(oldImport, newImport);
            modified = true;
            fixCount++;
          }
          break;
        }
      } catch (err) {
        console.error(`Error checking ${fullPath}:`, err);
      }
    }
  }
  
  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`Fixed ${fixCount} imports in: ${file}`);
    totalFixed += fixCount;
  }
});

console.log(`Total fixes: ${totalFixed}`);
