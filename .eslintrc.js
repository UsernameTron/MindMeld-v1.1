module.exports = {
  env: {
    node: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:prettier/recommended', // adds Prettier and turns off conflicting rules
  ],
  parserOptions: {
    ecmaVersion: 12,
  },
  rules: {
    'no-console': 'off',
    'comma-dangle': ['error', 'always-multiline'],
    quotes: ['error', 'single'],
    semi: ['error', 'always'],
    'no-var': 'error',
    'prefer-const': 'error',
  },
};
