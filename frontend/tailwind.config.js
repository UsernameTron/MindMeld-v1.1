const { tailwindTheme } = require('./src/design/tailwind.config');

module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: tailwindTheme,
  plugins: [],
  safelist: [
    // category-related classes that might be dynamically applied
    'bg-analyze-light',
    'bg-analyze-default',
    'bg-analyze-dark',
    'text-analyze-default',
    'text-analyze-dark',
    'border-analyze-default',
    'bg-chat-light',
    'bg-chat-default',
    'bg-chat-dark',
    'text-chat-default',
    'text-chat-dark',
    'border-chat-default',
    'bg-rewrite-light',
    'bg-rewrite-default',
    'bg-rewrite-dark',
    'text-rewrite-default',
    'text-rewrite-dark',
    'border-rewrite-default',
    'bg-persona-light',
    'bg-persona-default',
    'bg-persona-dark',
    'text-persona-default',
    'text-persona-dark',
    'border-persona-default',
  ],
};
