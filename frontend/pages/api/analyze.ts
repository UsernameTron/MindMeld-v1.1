import type { NextApiRequest, NextApiResponse } from 'next';

interface AnalysisResult {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  location?: {
    line: number;
    column: number;
  };
  code?: string;
  suggestion?: string;
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { code, language } = req.body;
    
    if (!code || !language) {
      return res.status(400).json({ message: 'Code and language are required' });
    }

    // Mock analysis logic
    const results: AnalysisResult[] = [];
    
    // Check common issues based on language
    if (language === 'javascript' || language === 'typescript') {
      if (code.includes('var ')) {
        results.push({
          id: '1',
          type: 'warning',
          message: 'Use of var is discouraged',
          location: {
            line: code.split('\n').findIndex((line: string) => line.includes('var ')) + 1,
            column: code.split('\n').find((line: string) => line.includes('var '))?.indexOf('var') || 0
          },
          suggestion: 'Use const or let instead'
        });
      }
      
      if (code.includes('console.log')) {
        results.push({
          id: '2',
          type: 'info',
          message: 'Console statement found',
          location: {
            line: code.split('\n').findIndex((line: string) => line.includes('console.log')) + 1,
            column: code.split('\n').find((line: string) => line.includes('console.log'))?.indexOf('console.log') || 0
          },
          suggestion: 'Remove console statements in production code'
        });
      }
      
      // Check for missing semicolons in JavaScript
      if (language === 'javascript' && /[^;\s]$/.test(code)) {
        results.push({
          id: '3',
          type: 'error',
          message: 'Missing semicolon',
          location: {
            line: code.split('\n').findIndex((line: string) => /[^;\s]$/.test(line)) + 1,
            column: code.split('\n').find((line: string) => /[^;\s]$/.test(line))?.length || 0
          },
          suggestion: 'Add semicolon at the end of the line'
        });
      }
    }
    
    if (language === 'python') {
      if (code.includes('print(')) {
        results.push({
          id: '4',
          type: 'info',
          message: 'Print statement found',
          location: {
            line: code.split('\n').findIndex((line: string) => line.includes('print(')) + 1,
            column: code.split('\n').find((line: string) => line.includes('print('))?.indexOf('print(') || 0
          }
        });
      }
    }
    
    // Add a success message if code looks good
    if (results.length === 0) {
      results.push({
        id: '5',
        type: 'success',
        message: 'No issues found. Your code looks great!'
      });
    }

    res.status(200).json({ results });
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ message: 'Failed to analyze code' });
  }
}
