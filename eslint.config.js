// eslint configuration file
import eslint from '@eslint/js';

export default [
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
