import CodeAnalyzer from '../../components/CodeAnalyzer/CodeAnalyzer.tsx';
import { Metadata } from 'next';
import Loading from './loading.tsx';

export const metadata: Metadata = {
  title: 'Code Analyzer | MindMeld',
  description: 'Analyze your code for issues, best practices, and improvements.',
  openGraph: {
    title: 'Code Analyzer | MindMeld',
    description: 'Analyze your code for issues, best practices, and improvements.',
    url: '/analyze',
    type: 'website',
  },
};

export default function AnalyzePage() {
  return <CodeAnalyzer />;
}
