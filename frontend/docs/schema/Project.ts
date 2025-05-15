// Project schema
export interface Project {
  id: string;
  title: string;
  description: string;
  codeSnippet: string;
  language: string;
  category: 'analyze' | 'chat' | 'rewrite' | 'persona';
  updatedAt: string;
  createdAt: string;
  ownerId: string;
}
