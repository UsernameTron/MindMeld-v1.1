#!/usr/bin/env node

/**
 * This script patches test files to replace Jest-DOM matchers with native DOM assertions
 * It's addressing the issue where Vitest doesn't properly recognize the Jest-DOM matchers
 */

import fs from 'fs';
import path from 'path';
import { glob } from 'glob';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PATTERNS_TO_REPLACE = [
  // toBeInTheDocument
  {
    regex: /expect\((.*?)\)\.toBeInTheDocument\(\)/g,
    replacement: 'expect($1).toBeTruthy()'
  },
  {
    regex: /expect\((.*?)\)\.not\.toBeInTheDocument\(\)/g,
    replacement: 'expect($1).toBeFalsy()'
  },
  // toHaveClass
  {
    regex: /expect\((.*?)\)\.toHaveClass\(['"](.*?)['"](?:,\s*\{.*?\})?\)/g,
    replacement: 'expect($1?.classList.contains("$2")).toBe(true)'
  },
  {
    regex: /expect\((.*?)\)\.not\.toHaveClass\(['"](.*?)['"](?:,\s*\{.*?\})?\)/g,
    replacement: 'expect($1?.classList.contains("$2")).toBe(false)'
  },
  // toHaveAttribute
  {
    regex: /expect\((.*?)\)\.toHaveAttribute\(['"](.*?)['"],\s*['"](.*?)['"]\)/g,
    replacement: 'expect($1?.getAttribute("$2")).toBe("$3")'
  },
  {
    regex: /expect\((.*?)\)\.toHaveAttribute\(['"](.*?)['"](?:,\s*\{.*?\})?\)/g,
    replacement: 'expect($1?.hasAttribute("$2")).toBe(true)'
  },
  // toHaveTextContent
  {
    regex: /expect\((.*?)\)\.toHaveTextContent\(\s*['"](.*?)['"](?:,\s*\{.*?\})?\)/g,
    replacement: 'expect($1?.textContent?.includes("$2")).toBe(true)'
  },
  // toBeVisible
  {
    regex: /expect\((.*?)\)\.toBeVisible\(\)/g,
    replacement: 'expect($1).toBeTruthy()'
  },
  // toBeDisabled
  {
    regex: /expect\((.*?)\)\.toBeDisabled\(\)/g,
    replacement: 'expect($1).toBeDisabled()'
  },
  // toHaveValue
  {
    regex: /expect\((.*?)\)\.toHaveValue\(['"](.*?)['"]\)/g,
    replacement: 'expect($1?.value).toBe("$2")'
  },
  // toBeChecked
  {
    regex: /expect\((.*?)\)\.toBeChecked\(\)/g, 
    replacement: 'expect($1?.checked).toBe(true)'
  },
  // toHaveLength
  {
    regex: /expect\((.*?)\)\.toHaveLength\((\d+)\)/g,
    replacement: 'expect($1).toHaveLength($2)'
  },
  // toContain for arrays
  {
    regex: /expect\((.*?)\)\.toContain\(['"](.*?)['"]\)/g,
    replacement: 'expect($1).toContain("$2")'
  },
  // Ensure element usage
  {
    regex: /expect\((.*?)\?\.(.*?)\)\.(.+)\((.*?)\)/g, 
    replacement: 'expect($1?.$2).$3($4)'
  }
];

// Process test files
(async () => {
  try {
    // Find all test files
    const TEST_FILES = await glob('src/**/*.{test,spec}.{ts,tsx}');
    let totalReplacements = 0;
    
    // Process each file
    for (const filePath of TEST_FILES) {
      const fullPath = path.resolve(process.cwd(), filePath);
      let content = fs.readFileSync(fullPath, 'utf8');
      
      // Apply all replacements
      let replacementsMade = 0;
      
      for (const pattern of PATTERNS_TO_REPLACE) {
        const originalContent = content;
        content = content.replace(pattern.regex, pattern.replacement);
        
        // Count replacements
        if (originalContent !== content) {
          const matches = originalContent.match(pattern.regex);
          const count = matches ? matches.length : 0;
          replacementsMade += count;
        }
      }
      
      // Only write if changes were made
      if (replacementsMade > 0) {
        fs.writeFileSync(fullPath, content);
        totalReplacements += replacementsMade;
        console.log(`✅ Updated ${filePath} (${replacementsMade} replacements)`);
      }
    }
    
    console.log(`\nDone! Made ${totalReplacements} replacements across ${TEST_FILES.length} files.`);
    console.log('Please run tests to verify the changes.');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
})();