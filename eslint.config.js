import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat({
  baseDirectory: process.cwd(),
  recommendedConfig: true
});

export default [
  // Load ESLint’s recommended rules and Prettier integration
  ...compat.extends('eslint:recommended', 'plugin:prettier/recommended'),
  {
    ignores: ['node_modules/**', 'dist/**'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module'
    },
    rules: {
      'no-console': 'off',
      'comma-dangle': ['error', 'always-multiline'],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'error'
    }
  }
];
