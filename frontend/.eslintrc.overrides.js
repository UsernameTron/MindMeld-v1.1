module.exports = {
  overrides: [
    // Override for test files to allow 'any' type
    {
      files: ['**/__tests__/**/*.ts', '**/__tests__/**/*.tsx', '**/*.test.ts', '**/*.test.tsx'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
      },
    },
    // Temporarily disable specific rules for specific files
    {
      files: ['src/utils/jwt.ts'],
      rules: {
        '@typescript-eslint/no-unused-vars': 'off',
      },
    },
  ],
};
