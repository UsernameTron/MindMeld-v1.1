# Code Editor Integration in Dashboard

Looking at your `CodeEditor` component, I can see it's well-structured with clear prop types and category styling that matches your planned features (analyze, chat, rewrite, persona). This component will be valuable in your dashboard implementation for Sprint 4.

## Dashboard Integration Suggestions

Here's how you could integrate this component into your Sprint 4 dashboard:

### 1. Code Preview Cards

```tsx
import React from 'react';
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
```

### 2. Recent Projects Section

For your dashboard home page, consider adding a section that displays recent code projects:

```tsx
import React from 'react';
import { CodePreviewCard } from '../../ui/molecules/CodePreviewCard';

export const RecentProjects: React.FC = () => {
  // This would eventually fetch from your API
  const recentProjects = [
    {
      id: '1',
      title: 'Authentication Service',
      description: 'JWT authentication implementation',
      codeSnippet: `const authenticate = async (credentials) => {\n  const response = await api.post('/auth/login', credentials);\n  return response.data.token;\n};`,
      language: 'javascript',
      category: 'analyze' as const,
      updatedAt: '2025-05-10T15:30:00Z'
    },
    // More projects...
  ];

  return (
    <div className="mb-8">
      <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {recentProjects.map(project => (
          <CodePreviewCard 
            key={project.id}
            title={project.title}
            description={`Last edited: ${new Date(project.updatedAt).toLocaleDateString()}`}
            codeSnippet={project.codeSnippet}
            language={project.language}
            category={project.category}
            onOpen={() => console.log(`Open project ${project.id}`)}
          />
        ))}
      </div>
    </div>
  );
};
```

## Improvements to CodeEditor Component

Consider these enhancements to your current CodeEditor component:

### 1. Add Theme Support

```tsx
// ...existing code...
export interface CodeEditorProps {
  // ...existing props...
  /** Editor theme */
  theme?: 'light' | 'dark' | 'system';
  // ...existing props...
}

const CodeEditor = forwardRef<any, CodeEditorProps>(({ 
  // ...existing props...
  theme = 'light',
  // ...existing props...
}, ref) => {
  // ...existing code...
  // Theme handling
  const [currentTheme, setCurrentTheme] = useState(theme === 'system' ? 
    (typeof window !== 'undefined' && 
     window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : theme);
  
  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        setCurrentTheme(e.matches ? 'dark' : 'light');
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      setCurrentTheme(theme);
    }
  }, [theme]);
  
  return (
    <div 
      className={`code-editor rounded-md overflow-hidden border ${categoryClasses[category]} ${sizeClasses[size]} ${className}`}
      data-testid="code-editor"
    >
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme={currentTheme === 'dark' ? 'vs-dark' : 'light'}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          folding: true,
          lineNumbers: 'on',
          readOnly,
          renderLineHighlight: 'all',
          ...options,
        }}
        className="min-h-[200px]"
      />
    </div>
  );
});
// ...existing code...
```

### 2. Add Loading State Customization

```tsx
// ...existing code...
export interface CodeEditorProps {
  // ...existing props...
  /** Custom loading component */
  loadingComponent?: React.ReactNode;
  // ...existing props...
}

// Dynamically import Monaco editor for better performance
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false, loading: ({ isLoading, error, retry }) => 
    isLoading ? (props.loadingComponent || 
      <div className="h-64 bg-gray-100 animate-pulse rounded-md" />) : null
  }
);
// ...existing code...
```

## Authentication Integration

Since you're implementing authentication in Sprint 4, ensure your CodeEditor is ready for authenticated contexts:

```tsx
// ...existing code...
import { useAuth } from '../../../../hooks/useAuth';

// In your CodeEditor component:
const { isAuthenticated } = useAuth();

// Add a subtle authentication indicator if needed
{!readOnly && !isAuthenticated && (
  <div className="absolute top-2 right-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
    Read-only: Sign in to edit
  </div>
)}
// ...existing code...
```

This gives you a foundation to integrate the CodeEditor into your Sprint 4 dashboard implementation while preparing for future features. Let me know if you'd like more specific guidance on any of these aspects!
