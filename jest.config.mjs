export default {
  roots: ['<rootDir>/src', '<rootDir>/__tests__'],
  testMatch: ['**/?(*.)+(spec|test).js'],
  testPathIgnorePatterns: [
    '/node_modules/',
    'promptService\\.test\\.js$', // skip Vitest test
  ],
  testEnvironment: 'node',
  transform: {
    '^.+\\.js$': ['babel-jest', { configFile: './babel.config.cjs', babelrc: false }],
  },
  moduleNameMapper: {},
};
