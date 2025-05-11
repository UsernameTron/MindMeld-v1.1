const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find all TypeScript files
const files = glob.sync('src/**/*.{ts,tsx}', { cwd: path.resolve(__dirname, '..') });

// Extensions to check
const extensions = ['.ts', '.tsx', '.js', '.jsx'];

files.forEach(file => {
  const filePath = path.resolve(__dirname, '..', file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Match import statements with relative paths
  const importRegex = /from\s+['"](\.[^'"]+)['"]/g;
  let match;
  let modified = false;
  
  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1];
    
    // Skip if already has extension
    if (path.extname(importPath)) continue;
    
    // Check file exists with various extensions
    for (const ext of extensions) {
      const fullPath = path.resolve(path.dirname(filePath), `${importPath}${ext}`);
      if (fs.existsSync(fullPath)) {
        // Replace import path with extension
        const newContent = content.replace(
          `from '${importPath}'`,
          `from '${importPath}${ext}'`
        );
        if (newContent !== content) {
          content = newContent;
          modified = true;
        }
        break;
      }
    }
  }
  
  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`Fixed imports in: ${file}`);
  }
});
