import baseTokens from './base.js';

export const lightTheme = {
  ...baseTokens,
  background: {
    primary: baseTokens.colors.neutral[50],
    secondary: baseTokens.colors.neutral[100],
    tertiary: baseTokens.colors.neutral[200],
  },
  text: {
    primary: baseTokens.colors.neutral[900],
    secondary: baseTokens.colors.neutral[700],
    tertiary: baseTokens.colors.neutral[500],
    inverse: baseTokens.colors.neutral[50],
  },
  border: {
    light: baseTokens.colors.neutral[200],
    default: baseTokens.colors.neutral[300],
    dark: baseTokens.colors.neutral[400],
  },
};

export const darkTheme = {
  ...baseTokens,
  background: {
    primary: baseTokens.colors.neutral[900],
    secondary: baseTokens.colors.neutral[800],
    tertiary: baseTokens.colors.neutral[700],
  },
  text: {
    primary: baseTokens.colors.neutral[50],
    secondary: baseTokens.colors.neutral[200],
    tertiary: baseTokens.colors.neutral[400],
    inverse: baseTokens.colors.neutral[900],
  },
  border: {
    light: baseTokens.colors.neutral[700],
    default: baseTokens.colors.neutral[600],
    dark: baseTokens.colors.neutral[500],
  },
};
