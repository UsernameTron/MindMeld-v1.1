'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { useSettings, Settings, DEFAULT_SETTINGS } from '@/hooks/useSettings';

// Define context shape
interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  updateAnalyzerSettings: (analyzerSettings: Partial<Settings['analyzer']>) => void;
  resetSettings: () => void;
}

// Create context with default values
const SettingsContext = createContext<SettingsContextType>({
  settings: DEFAULT_SETTINGS,
  updateSettings: () => {},
  updateAnalyzerSettings: () => {},
  resetSettings: () => {},
});

// Custom hook to use the settings context
export const useSettingsContext = () => useContext(SettingsContext);

// Provider component that wraps app or layout
export const SettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Use the hook to get settings and methods
  const { settings, updateSettings, updateAnalyzerSettings, resetSettings } = useSettings();

  // Value object to be provided to consumers
  const value = {
    settings,
    updateSettings,
    updateAnalyzerSettings,
    resetSettings,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};