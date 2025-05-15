import React, { useState, useMemo } from 'react';
import { promptApi } from '../../src/services/promptApi';
import { TemplateSelector, ParameterForm, PromptDisplay } from '../components/mindmeld';
import type { PromptTemplate, AdvancedPromptTemplate } from '../../src/types/promptTypes';

const PromptPage: React.FC = () => {
  const templates = useMemo(() => promptApi.getTemplates().filter(t => 'parameters' in t), []);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [prompt, setPrompt] = useState<string>('');
  const [error, setError] = useState<string>('');

  const selectedTemplate = useMemo<AdvancedPromptTemplate | null>(() => {
    if (!selectedId) return null;
    const tpl = promptApi.getTemplateById(selectedId);
    return tpl && 'parameters' in tpl ? (tpl as AdvancedPromptTemplate) : null;
  }, [selectedId]);

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setParamValues({});
    setPrompt('');
    setError('');
  };

  const handleParamChange = (id: string, value: string) => {
    setParamValues(prev => ({ ...prev, [id]: value }));
  };

  const handleGenerate = () => {
    if (!selectedTemplate) return;
    try {
      setError('');
      const result = promptApi.generatePrompt(selectedTemplate.id, paramValues);
      setPrompt(result);
    } catch (e: any) {
      setPrompt('');
      setError(e.message);
    }
  };

  return (
    <main className="mm-prompt-page">
      <h1>MindMeld Prompt Generator</h1>
      <TemplateSelector
        templates={templates}
        selectedId={selectedId}
        onSelect={handleSelect}
      />
      {selectedTemplate && (
        <ParameterForm
          template={selectedTemplate}
          values={paramValues}
          onChange={handleParamChange}
          onSubmit={handleGenerate}
          error={error}
        />
      )}
      {prompt && <PromptDisplay prompt={prompt} />}
    </main>
  );
};

export default PromptPage;
