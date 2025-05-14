import type { NextApiRequest, NextApiResponse } from 'next';

export interface Project {
  id: string;
  title: string;
  description: string;
  codeSnippet: string;
  language: string;
  category: 'analyze' | 'chat' | 'rewrite' | 'persona';
  updatedAt: string;
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // In production, you would fetch this from a database
  const recentProjects: Project[] = [
    {
      id: '1',
      title: 'Authentication Service',
      description: 'JWT token-based auth implementation',
      codeSnippet: `const authenticate = async (credentials) => {\n  const response = await api.post('/auth/login', credentials);\n  return response.data.token;\n};`,
      language: 'javascript',
      category: 'analyze',
      updatedAt: new Date().toISOString()
    },
    {
      id: '2',
      title: 'Input Validation',
      description: 'Form validation utilities',
      codeSnippet: `function validateEmail(email) {\n  const regex = /[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n  return regex.test(email);\n}`,
      language: 'javascript',
      category: 'rewrite',
      updatedAt: new Date(Date.now() - 86400000).toISOString() // 1 day ago
    }
  ];

  res.status(200).json(recentProjects);
}
