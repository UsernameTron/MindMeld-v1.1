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
    const loadProjects = async () => {
      try {
        const projects = await projectService.getRecentProjects();
        setRecentProjects(projects);
      } catch (err) {
        setError('Failed to load recent projects');
        console.error(err);
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
        <div className="mb-10">
          <h2 className="text-xl font-semibold mb-4">Features</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              title="Code Analyzer"
              description="Analyze your code for errors, warnings, and best practices."
              icon={<CodeBracketIcon className="w-7 h-7 text-blue-500" />}
              href="/analyze"
              category="analyze"
            />
            <FeatureCard
              title="Chat Interface"
              description="Discuss your code with advanced AI assistants."
              icon={<ChatBubbleLeftRightIcon className="w-7 h-7 text-green-500" />}
              href="/chat"
              category="chat"
              comingSoon
            />
            <FeatureCard
              title="Code Rewriter"
              description="Automatically improve and refactor your code."
              icon={<PencilSquareIcon className="w-7 h-7 text-purple-500" />}
              href="/rewrite"
              category="rewrite"
              comingSoon
            />
            <FeatureCard
              title="Persona Generator"
              description="Create custom AI personas for specific tasks."
              icon={<UserCircleIcon className="w-7 h-7 text-yellow-500" />}
              href="/persona"
              category="persona"
              comingSoon
            />
          </div>
        </div>

        {/* Recent Projects Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Recent Projects</h2>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-pulse h-8 w-8 bg-gray-200 rounded-full"></div>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 text-red-700 rounded">
              {error}
            </div>
          ) : recentProjects.length === 0 ? (
            <div className="p-4 bg-gray-50 text-gray-500 rounded">
              No recent projects found. Start by analyzing some code!
            </div>
          ) : (
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
          )}
        </div>
      </DashboardLayout>
    </RequireAuth>
  );
}
