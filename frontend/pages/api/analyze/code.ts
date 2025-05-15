import type { NextApiRequest, NextApiResponse } from 'next';

interface CodeQualityIssue {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
  details?: string;
}

interface CodeAnalysisResult {
  issues: CodeQualityIssue[];
  complexity_score: number;
  optimization_suggestions: string[];
  performance_issues: Array<Record<string, string>>;
  language: string;
  summary: string;
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<CodeAnalysisResult | { error: string }>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { code, language, options } = req.body;
    
    if (!code || !language) {
      return res.status(400).json({ error: 'Code and language are required' });
    }

    // Initialize the result structure
    const result: CodeAnalysisResult = {
      issues: [],
      complexity_score: 1,
      optimization_suggestions: [],
      performance_issues: [],
      language,
      summary: `Analysis of ${language.toUpperCase()} code complete`
    };
    
    // Check common issues based on language
    if (language === 'javascript' || language === 'typescript') {
      // Check for var usage
      if (code.includes('var ')) {
        result.issues.push({
          line: code.split('\n').findIndex(line => line.includes('var ')) + 1,
          column: code.split('\n').find(line => line.includes('var '))?.indexOf('var') || 0,
          message: 'Use of var is discouraged',
          severity: 'warning',
          suggestion: 'Use const or let instead',
          details: 'Using var can lead to unexpected behavior due to function-scoping instead of block-scoping.'
        });
        
        result.optimization_suggestions.push('Replace var with const for variables that are not reassigned');
      }
      
      // Check for console statements
      if (code.includes('console.log')) {
        result.issues.push({
          line: code.split('\n').findIndex(line => line.includes('console.log')) + 1,
          column: code.split('\n').find(line => line.includes('console.log'))?.indexOf('console.log') || 0,
          message: 'Console statement found',
          severity: 'info',
          suggestion: 'Consider removing console statements in production code',
          details: 'Console statements can impact performance in production and expose sensitive information.'
        });
      }
      
      // Check for missing semicolons in JavaScript
      if (language === 'javascript') {
        const lines = code.split('\n');
        lines.forEach((line, index) => {
          // Simple check for lines that might need semicolons
          if (line.trim().length > 0 && !line.trim().endsWith(';') && !line.trim().match(/[{}[\](),:?]$/)) {
            result.issues.push({
              line: index + 1,
              column: line.length,
              message: 'Missing semicolon',
              severity: 'error',
              suggestion: 'Add semicolon at the end of the line',
              details: 'Missing semicolons can lead to unexpected behavior due to automatic semicolon insertion.'
            });
          }
        });
      }
      
      // Check for unused variables (simple implementation)
      const varPattern = /(const|let|var)\s+(\w+)\s*=/g;
      let match;
      while ((match = varPattern.exec(code)) !== null) {
        const varName = match[2];
        const varDeclarationIndex = match.index;
        const usageCount = (code.match(new RegExp(`\\b${varName}\\b`, 'g')) || []).length;
        
        if (usageCount === 1) { // Only the declaration itself
          const lineIndex = code.substring(0, varDeclarationIndex).split('\n').length - 1;
          result.issues.push({
            line: lineIndex + 1,
            column: match[0].indexOf(varName),
            message: `Unused variable: ${varName}`,
            severity: 'warning',
            suggestion: `Remove the unused variable ${varName}`,
            details: 'Unused variables increase code size and can indicate logical errors or forgotten code.'
          });
        }
      }
      
      // Performance suggestions
      if (code.includes('for (') && !code.includes('for (const ')) {
        result.optimization_suggestions.push('Use for...of or Array methods instead of traditional for loops');
      }
      
      if (code.includes('.forEach(') && language === 'javascript') {
        result.performance_issues.push({
          message: 'forEach() may have performance implications',
          suggestion: 'Consider using for...of loops for better performance',
          impact: 'low'
        });
      }
    }
    
    // Python-specific checks
    if (language === 'python') {
      // Check for print statements
      if (code.includes('print(')) {
        result.issues.push({
          line: code.split('\n').findIndex(line => line.includes('print(')) + 1,
          column: code.split('\n').find(line => line.includes('print('))?.indexOf('print(') || 0,
          message: 'Print statement found',
          severity: 'info',
          suggestion: 'Consider using logging instead of print for better control',
          details: 'In production code, structured logging provides better control and filtering capabilities.'
        });
      }
      
      // Check for indentation issues (simple check)
      const lines = code.split('\n');
      lines.forEach((line, index) => {
        if (line.trim() && line.startsWith(' ') && !line.startsWith('    ')) {
          result.issues.push({
            line: index + 1,
            column: 0,
            message: 'Inconsistent indentation',
            severity: 'error',
            suggestion: 'Use 4 spaces for indentation',
            details: 'PEP 8 recommends using 4 spaces per indentation level.'
          });
        }
      });
    }
    
    // Java-specific checks
    if (language === 'java') {
      // Check for System.out.println
      if (code.includes('System.out.println')) {
        result.issues.push({
          line: code.split('\n').findIndex(line => line.includes('System.out.println')) + 1,
          column: code.split('\n').find(line => line.includes('System.out.println'))?.indexOf('System.out.println') || 0,
          message: 'System.out.println found',
          severity: 'info',
          suggestion: 'Use a logging framework instead of System.out.println',
          details: 'For production code, a logging framework provides better control and configuration options.'
        });
      }
    }

    // C++ specific checks
    if (language === 'cpp') {
      // Check for using namespace std
      if (code.includes('using namespace std')) {
        result.issues.push({
          line: code.split('\n').findIndex(line => line.includes('using namespace std')) + 1,
          column: code.split('\n').find(line => line.includes('using namespace std'))?.indexOf('using namespace std') || 0,
          message: 'using namespace std is discouraged',
          severity: 'warning',
          suggestion: 'Use std:: prefix instead',
          details: 'Using namespace std can cause name conflicts and is generally considered bad practice.'
        });
      }
    }
    
    // Calculate a mock complexity score based on issues
    result.complexity_score = Math.max(1, Math.min(10, result.issues.length + 1));
    
    // Generate a summary
    if (result.issues.length === 0) {
      result.summary = `No issues found in your ${language} code. Great job!`;
    } else {
      const errorCount = result.issues.filter(issue => issue.severity === 'error').length;
      const warningCount = result.issues.filter(issue => issue.severity === 'warning').length;
      const infoCount = result.issues.filter(issue => issue.severity === 'info').length;
      
      result.summary = `Found ${errorCount} errors, ${warningCount} warnings, and ${infoCount} suggestions in your ${language} code.`;
    }

    // Add a 500ms delay to simulate network latency
    setTimeout(() => {
      res.status(200).json(result);
    }, 500);
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ error: 'Failed to analyze code' });
  }
}