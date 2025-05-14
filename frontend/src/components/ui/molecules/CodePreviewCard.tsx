import React from 'react';
// TODO: Ensure the Card component exists at the correct path.
// If it does not exist, create it at '../atoms/Card.tsx' or update the import path below.
import { Card } from '../atoms/Card';
import CodeEditor from '../organisms/CodeEditor/CodeEditor';

interface CodePreviewCardProps {
  title: string;
  description: string;
  codeSnippet: string;
  language: string;
  category: 'analyze' | 'chat' | 'rewrite' | 'persona';
  onOpen?: () => void;
}

export const CodePreviewCard: React.FC<CodePreviewCardProps> = ({
  title,
  description,
  codeSnippet,
  language,
  category,
  onOpen
}) => {
  return (
    <Card className="overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      
      <div className="h-48 overflow-hidden">
        <CodeEditor
          value={codeSnippet}
          language={language}
          readOnly={true}
          height="100%"
          category={category}
          options={{ 
            lineNumbers: 'off',
            minimap: { enabled: false }
          }}
        />
      </div>
      
      {onOpen && (
        <div className="p-3 bg-gray-50 text-right">
          <button 
            onClick={onOpen}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            View Full Code
          </button>
        </div>
      )}
    </Card>
  );
};
