import { components } from './generated/api-types.js';

// Extract schema types for easier usage
export type Schemas = components['schemas'];

// Common types
export type User = Schemas['User'];
export type AnalysisResult = Schemas['AnalysisResult'];
export type Card = Schemas['Card'];

// Add more type exports as needed for specific entities
