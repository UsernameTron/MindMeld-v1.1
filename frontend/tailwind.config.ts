import type { Config } from 'tailwindcss';
import baseTokens from './src/design/tokens/base.js';

const twConfig: Config = {
  content: [
    './src/**/*.{js, ts, jsx, tsx}',
    './pages/**/*.{js, ts, jsx, tsx}',
  ],
  theme: {
    extend: {
      colors: baseTokens.colors,
      spacing: baseTokens.spacing,
      fontFamily: baseTokens.typography.fontFamily,
      fontSize: baseTokens.typography.fontSize,
      fontWeight: baseTokens.typography.fontWeight,
      lineHeight: baseTokens.typography.lineHeight,
      borderRadius: baseTokens.borderRadius,
      boxShadow: baseTokens.boxShadow,
      // Add more mappings as needed
    },
  },
  plugins: [],
};

export default twConfig;
