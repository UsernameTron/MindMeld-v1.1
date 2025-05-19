// eslint configuration file

export default [
  {
    ignores: ['node_modules\\**', 'dist\\**'],
    languageOptions: {
      // Using ES2021 for compatibility with modern JavaScript features like logical assignment operators and String.prototype.replaceAll
      ecmaVersion: 2021,
      sourceType: 'module'
    },
    rules: {
      'comma-dangle': ['error', 'always-multiline'],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'error'
    }
  }
];
