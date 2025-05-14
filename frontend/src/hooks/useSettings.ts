'use client';

import { useState, useEffect } from 'react';
import { type SupportedLanguage } from '@/services/analysisService';

// Storage key constant
const STORAGE_KEY = 'mindmeld_settings';

// Ruleset type for analyzer configuration
export type AnalyzerRuleset = 'standard' | 'strict' | 'performance' | 'security' | 'custom';

// Settings interface with typed properties
export interface Settings {
  analyzer: {
    language: SupportedLanguage;
    theme: 'light' | 'dark' | 'system';
    debounceMs: number;
    autoAnalyze: boolean;
    rulesets: AnalyzerRuleset[];
    customRules: {
      ignoredWarnings: string[];
      ignoredCategories: string[];
    };
    fontSize: number;
    showLineNumbers: boolean;
    wordWrap: boolean;
    initialCode: string;
    lastCode?: string; // Stores the most recent code for persistence
  };
  // We could add more settings categories here in the future
  // ui: {...}
  // editor: {...}
}

// Default settings that will be used for initialization
export const DEFAULT_SETTINGS: Settings = {
  analyzer: {
    language: 'javascript',
    theme: 'system',
    debounceMs: 500,
    autoAnalyze: false,
    rulesets: ['standard'],
    customRules: {
      ignoredWarnings: [],
      ignoredCategories: [],
    },
    fontSize: 14,
    showLineNumbers: true,
    wordWrap: true,
    initialCode: '// Enter your code here\nfunction example() {\n  const unused = "test";\n  return "Hello world";\n}',
  },
};

/**
 * Hook to get and update user settings with localStorage persistence
 */
export function useSettings(): {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  updateAnalyzerSettings: (analyzerSettings: Partial<Settings['analyzer']>) => void;
  resetSettings: () => void;
} {
  // Initialize with default settings
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  
  // Load settings from localStorage on mount
  useEffect(() => {
    // Guard against SSR
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      const storedSettings = localStorage.getItem(STORAGE_KEY);
      if (storedSettings) {
        const parsedSettings = JSON.parse(storedSettings);
        // Merge stored settings with defaults to handle missing properties
        setSettings(mergeSettings(DEFAULT_SETTINGS, parsedSettings));
      }
    } catch (error) {
      console.error('Failed to load settings from localStorage:', error);
      // Fall back to defaults on error
      setSettings(DEFAULT_SETTINGS);
    }
  }, []);
  
  // Helper to deeply merge settings objects
  const mergeSettings = (defaultSettings: Settings, userSettings: Partial<Settings>): Settings => {
    // Deep copy the default settings
    const result = JSON.parse(JSON.stringify(defaultSettings)) as Settings;
    
    // Only handle analyzer settings for now, can be expanded for more categories
    if (userSettings.analyzer) {
      result.analyzer = {
        ...result.analyzer,
        ...userSettings.analyzer,
        // Handle nested objects
        customRules: {
          ...result.analyzer.customRules,
          ...(userSettings.analyzer.customRules || {})
        }
      };
    }
    
    return result;
  };
  
  // Update settings and persist to localStorage
  const updateSettings = (newSettings: Partial<Settings>) => {
    setSettings(prevSettings => {
      // Merge new settings with existing settings
      const updatedSettings = mergeSettings(prevSettings, newSettings);
      
      // Persist to localStorage with SSR guard
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSettings));
          
          // Log for debugging during development
          if (process.env.NODE_ENV === 'development') {
            console.log('Settings saved to localStorage:', {
              key: STORAGE_KEY,
              value: updatedSettings,
              lastCode: updatedSettings.analyzer.lastCode ? 
                `${updatedSettings.analyzer.lastCode.substring(0, 20)}...` : 
                'not set'
            });
          }
        } catch (error) {
          console.error('Failed to save settings to localStorage:', error);
        }
      }
      
      return updatedSettings;
    });
  };
  
  // Convenience method to update only analyzer settings
  const updateAnalyzerSettings = (analyzerSettings: Partial<Settings['analyzer']>) => {
    updateSettings({
      analyzer: analyzerSettings
    });
  };
  
  // Reset settings to defaults
  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
    
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (error) {
        console.error('Failed to remove settings from localStorage:', error);
      }
    }
  };
  
  return {
    settings,
    updateSettings,
    updateAnalyzerSettings,
    resetSettings
  };
}