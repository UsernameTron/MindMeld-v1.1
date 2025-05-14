'use client';

import React from 'react';
import { useSettingsContext } from '@/context/SettingsContext';
import { type AnalyzerRuleset } from '@/hooks/useSettings';
import { LoadingIndicator } from '../LoadingIndicator/LoadingIndicator';
import { ErrorDisplay } from '../ErrorDisplay/ErrorDisplay';
import { Button } from '../../../atoms/Button';
import { cn } from '@/utils/cn';

interface AnalyzerSettingsProps {
  supportedLanguages: { id: string, name: string }[];
  isLoadingLanguages?: boolean;
  onAnalyze?: () => void;
  isAnalyzing?: boolean;
  className?: string;
}

/**
 * Component for configuring analyzer settings
 */
export const AnalyzerSettings: React.FC<AnalyzerSettingsProps> = ({
  supportedLanguages = [],
  isLoadingLanguages = false,
  onAnalyze,
  isAnalyzing = false,
  className,
}) => {
  const { settings, updateAnalyzerSettings } = useSettingsContext();
  const { analyzer } = settings;

  // Map of available rulesets with display names
  const availableRulesets: Record<AnalyzerRuleset, string> = {
    standard: 'Standard',
    strict: 'Strict',
    performance: 'Performance',
    security: 'Security',
    custom: 'Custom',
  };

  // Toggle a ruleset in the array
  const toggleRuleset = (ruleset: AnalyzerRuleset) => {
    const currentRulesets = [...analyzer.rulesets];
    
    if (currentRulesets.includes(ruleset)) {
      // Remove the ruleset if already selected
      updateAnalyzerSettings({
        rulesets: currentRulesets.filter(r => r !== ruleset)
      });
    } else {
      // Add the ruleset
      updateAnalyzerSettings({
        rulesets: [...currentRulesets, ruleset]
      });
    }
  };

  // Toggle a simple boolean setting
  const toggleSetting = (setting: keyof typeof analyzer) => {
    if (typeof analyzer[setting] === 'boolean') {
      updateAnalyzerSettings({
        [setting]: !analyzer[setting]
      } as any);
    }
  };

  return (
    <div className={cn("bg-slate-50 dark:bg-slate-800 p-4 rounded-md border border-slate-200 dark:border-slate-700", className)}
         data-testid="analyzer-settings">
      <h2 className="text-lg font-semibold mb-4">Analysis Settings</h2>
      
      {/* Language Selection */}
      <div className="mb-4">
        <label htmlFor="language-select" className="block text-sm font-medium mb-1">
          Language
        </label>
        {isLoadingLanguages ? (
          <LoadingIndicator variant="spinner" size="sm" category="analyze" />
        ) : (
          <select
            id="language-select"
            data-testid="language-select"
            value={analyzer.language}
            onChange={(e) => updateAnalyzerSettings({ language: e.target.value as any })}
            className="w-full px-3 py-2 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 text-sm"
            disabled={isAnalyzing}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Theme Setting */}
      <div className="mb-4">
        <label htmlFor="theme-select" className="block text-sm font-medium mb-1">
          Editor Theme
        </label>
        <select
          id="theme-select"
          data-testid="theme-select"
          value={analyzer.theme}
          onChange={(e) => updateAnalyzerSettings({ theme: e.target.value as any })}
          className="w-full px-3 py-2 bg-white dark:bg-slate-700 rounded-md border border-slate-300 dark:border-slate-600 text-sm"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
      </div>

      {/* Font Size Slider */}
      <div className="mb-4">
        <label htmlFor="font-size-slider" className="block text-sm font-medium mb-1">
          Font Size: {analyzer.fontSize}px
        </label>
        <input
          id="font-size-slider"
          type="range"
          min="10"
          max="24"
          step="1"
          value={analyzer.fontSize}
          onChange={(e) => updateAnalyzerSettings({ fontSize: Number(e.target.value) })}
          className="w-full"
        />
      </div>

      {/* Debounce Slider */}
      <div className="mb-4">
        <label htmlFor="debounce-slider" className="block text-sm font-medium mb-1">
          Analysis Delay: {analyzer.debounceMs}ms
        </label>
        <input
          id="debounce-slider"
          type="range"
          min="0"
          max="2000"
          step="100"
          value={analyzer.debounceMs}
          onChange={(e) => updateAnalyzerSettings({ debounceMs: Number(e.target.value) })}
          className="w-full"
        />
      </div>

      {/* Auto-Analyze Toggle */}
      <div className="mb-4">
        <label className="flex items-center text-sm font-medium cursor-pointer">
          <input
            type="checkbox"
            checked={analyzer.autoAnalyze}
            onChange={() => toggleSetting('autoAnalyze')}
            className="mr-2"
          />
          Auto-Analyze
        </label>
      </div>

      {/* Word Wrap Toggle */}
      <div className="mb-4">
        <label className="flex items-center text-sm font-medium cursor-pointer">
          <input
            type="checkbox"
            checked={analyzer.wordWrap}
            onChange={() => toggleSetting('wordWrap')}
            className="mr-2"
          />
          Word Wrap
        </label>
      </div>

      {/* Line Numbers Toggle */}
      <div className="mb-4">
        <label className="flex items-center text-sm font-medium cursor-pointer">
          <input
            type="checkbox"
            checked={analyzer.showLineNumbers}
            onChange={() => toggleSetting('showLineNumbers')}
            className="mr-2"
          />
          Show Line Numbers
        </label>
      </div>

      {/* Rulesets Group */}
      <div className="mb-6">
        <p className="text-sm font-medium mb-2">Rulesets</p>
        <div className="space-y-2">
          {Object.entries(availableRulesets).map(([ruleset, displayName]) => (
            <label key={ruleset} className="flex items-center text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={analyzer.rulesets.includes(ruleset as AnalyzerRuleset)}
                onChange={() => toggleRuleset(ruleset as AnalyzerRuleset)}
                className="mr-2"
              />
              {displayName}
            </label>
          ))}
        </div>
      </div>

      {/* Analyze Button */}
      {onAnalyze && (
        <Button 
          data-testid="analyze-btn"
          onClick={onAnalyze} 
          disabled={isAnalyzing}
          className="w-full"
        >
          {isAnalyzing ? <LoadingIndicator size="sm" /> : 'Analyze Code'}
        </Button>
      )}
    </div>
  );
};

export default AnalyzerSettings;