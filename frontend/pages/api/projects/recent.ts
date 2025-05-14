import type { NextApiRequest, NextApiResponse } from 'next';
import { verifyToken } from '../../../src/utils/jwt';

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
  console.log('API projects/recent: Processing request');
  
  if (req.method !== 'GET') {
    console.log('API projects/recent: Method not allowed');
    return res.status(405).json({ message: `Method ${req.method} not allowed` });
  }
  
  // Check for auth_token cookie
  const authToken = req.cookies.auth_token;
  console.log('API projects/recent: Auth token present:', !!authToken);
  
  if (!authToken) {
    console.log('API projects/recent: No auth_token cookie found');
    return res.status(401).json({ message: 'Authentication required' });
  }
  
  // Verify the token
  try {
    console.log('API projects/recent: Verifying token');
    const payload = verifyToken(authToken);
    
    if (!payload) {
      console.log('API projects/recent: Invalid or expired token');
      return res.status(401).json({ message: 'Invalid or expired token' });
    }

    console.log('API projects/recent: Authentication successful for user:', payload.email);
    
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
        updatedAt: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        title: 'Data Visualization',
        description: 'Chart rendering component',
        codeSnippet: `class BarChart extends Component {\n  render() {\n    return <canvas ref={this.chartRef} width="400" height="200"></canvas>;\n  }\n}`,
        language: 'javascript',
        category: 'chat',
        updatedAt: new Date(Date.now() - 172800000).toISOString()
      }
    ];

    console.log('API projects/recent: Returning projects, count:', recentProjects.length);
    return res.status(200).json(recentProjects);
  } catch (error) {
    console.error('API projects/recent: Error processing request:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
