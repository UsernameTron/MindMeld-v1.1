import React, { useState, useEffect } from 'react';
import { RequireAuth } from '../src/components/auth/RequireAuth';
import { DashboardLayout } from '../src/components/layout/DashboardLayout';
import { CodePreviewCard } from '../src/components/ui/molecules/CodePreviewCard';
import { FeatureCard } from '../src/components/ui/molecules/FeatureCard';
import { ChatBubbleLeftRightIcon, CodeBracketIcon, PencilSquareIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { projectService } from '../src/services/projectService';
import type { Project } from '../pages/api/projects/recent';
import { withAuthSSR } from '../src/utils/auth';

export const getServerSideProps = withAuthSSR();

export default function DashboardPage() {
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('Dashboard: Loading projects data');
    const loadProjects = async () => {
      try {
        const projects = await projectService.getRecentProjects();
        console.log('Dashboard: Loaded projects:', projects);
        setRecentProjects(projects);
      } catch (err) {
        console.error('Dashboard: Failed to load projects:', err);
        setError('Failed to load recent projects');
      } finally {
        setIsLoading(false);
      }
    };
    loadProjects();
  }, []);

  return (
    <RequireAuth>
      <DashboardLayout>
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Welcome to MindMeld</h1>
          <p className="text-gray-600">Your coding assistant dashboard</p>
        </div>

        {/* Features Section */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <FeatureCard 
              title="Code Analysis" 
              description="Analyze your code for patterns and improvements"
              icon={<CodeBracketIcon className="h-6 w-6" />}
              category="analyze"
              href="/analyze"
            />
            <FeatureCard 
              title="AI Chat" 
              description="Chat with AI about your code"
              icon={<ChatBubbleLeftRightIcon className="h-6 w-6" />}
              category="chat"
              href="/chat"
            />
            <FeatureCard 
              title="Code Rewrite" 
              description="Get suggestions for rewriting and improving code"
              icon={<PencilSquareIcon className="h-6 w-6" />}
              category="rewrite"
              href="/rewrite"
            />
            <FeatureCard 
              title="AI Personas" 
              description="Chat with different AI personas"
              icon={<UserCircleIcon className="h-6 w-6" />}
              category="persona"
              href="/personas"
            />
          </div>
        </section>

        {/* Recent Projects Section */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
          {isLoading ? (
            <div className="text-center py-4">Loading recent projects...</div>
          ) : error ? (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <p className="text-red-700">{error}</p>
            </div>
          ) : recentProjects.length === 0 ? (
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <p className="text-blue-700">No recent projects found. Create one to get started!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {recentProjects.map((project) => (
                <CodePreviewCard
                  key={project.id}
                  title={project.title}
                  description={project.description}
                  language={project.language}
                  codeSnippet={project.codeSnippet}
                  category={project.category}
                />
              ))}
            </div>
          )}
        </section>
      </DashboardLayout>
    </RequireAuth>
  );
}
