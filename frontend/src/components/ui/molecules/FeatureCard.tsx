import React from 'react';
import Link from 'next/link';

export interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  category: 'analyze' | 'chat' | 'rewrite' | 'persona';
  comingSoon?: boolean;
  className?: string;
}

const categoryStyles: Record<string, string> = {
  analyze: 'border-blue-500 hover:bg-blue-50',
  chat: 'border-green-500 hover:bg-green-50',
  rewrite: 'border-purple-500 hover:bg-purple-50',
  persona: 'border-yellow-500 hover:bg-yellow-50',
};

export const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  href,
  category,
  comingSoon = false,
  className = '',
}) => {
  const borderClass = categoryStyles[category] || 'border-gray-300';
  const content = (
    <div
      className={`flex flex-col h-full border-l-4 ${borderClass} rounded-lg bg-white shadow transition-colors duration-200 ${
        comingSoon ? 'opacity-60 grayscale pointer-events-none' : 'cursor-pointer'
      } ${className}`}
    >
      <div className="p-5 flex-1 flex flex-col">
        <div className="flex items-center mb-3">
          <span className="mr-3">{icon}</span>
          <h3 className="text-lg font-semibold">{title}</h3>
          {comingSoon && (
            <span className="ml-2 px-2 py-1 text-xs bg-gray-200 rounded-full">Coming Soon</span>
          )}
        </div>
        <p className="text-gray-600 flex-1">{description}</p>
      </div>
    </div>
  );

  if (comingSoon) {
    return content;
  }
  return (
    <Link href={href} className="block h-full">
      {content}
    </Link>
  );
};

export default FeatureCard;
