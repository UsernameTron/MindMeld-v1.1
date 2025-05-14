import { useState } from 'react';
import { RequireAuth } from '../src/components/auth/RequireAuth';
import { DashboardLayout } from '../src/components/layout/DashboardLayout';
import CodeEditor from '../src/components/ui/organisms/CodeEditor/CodeEditor';
import { withAuthSSR } from '../src/utils/auth';
import { useAuth } from '../src/context/AuthContext';
import { apiService } from '../src/services/apiService';

export default function AnalyzePage() {
  const { isAuthenticated } = useAuth();
  const [code, setCode] = useState('// Enter your code here');
  const [language, setLanguage] = useState('javascript');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    try {
      const response = await apiService.post<any>('/analyze', { code, language });
      setResults((response as any).results || []);
    } catch (err) {
      setError('Analysis failed. Please try again.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <RequireAuth>
      <DashboardLayout>
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Code Analyzer</h1>
          <p className="text-gray-600">Analyze your code for improvements</p>
        </div>
        <div className="mb-4 flex gap-4">
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-3 py-2 border rounded"
          >
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
          </select>
          <button 
            onClick={handleAnalyze}
            disabled={isAnalyzing || !isAuthenticated}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Code'}
          </button>
        </div>
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Editor */}
          <div className="border rounded overflow-hidden">
            <CodeEditor 
              value={code}
              onChange={(v) => setCode(v ?? '')}
              language={language}
              category="analyze"
              height="400px"
              theme="system"
            />
          </div>
          {/* Results */}
          <div className="border rounded overflow-hidden bg-gray-50 p-4">
            <h2 className="text-lg font-medium mb-4">Analysis Results</h2>
            {isAnalyzing ? (
              <div className="flex justify-center py-8">
                <div className="animate-pulse h-8 w-8 bg-gray-200 rounded-full"></div>
              </div>
            ) : results.length === 0 ? (
              <p className="text-gray-500">No results yet. Click "Analyze Code" to begin.</p>
            ) : (
              <ul className="space-y-3">
                {results.map((result, index) => (
                  <li key={index} className="p-3 bg-white border rounded">
                    <p className="font-medium">{result.message}</p>
                    {result.location && (
                      <p className="text-sm text-gray-500">
                        Line {result.location.line}, Column {result.location.column}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </DashboardLayout>
    </RequireAuth>
  );
}

// Add server-side protection
export const getServerSideProps = withAuthSSR();
