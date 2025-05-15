import React from 'react';
import './styles/PromptDisplay.css';

export interface PromptDisplayProps {
  prompt: string;
  onCopy?: () => void;
}

export const PromptDisplay: React.FC<PromptDisplayProps> = ({ prompt, onCopy }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(prompt);
    if (onCopy) onCopy();
  };

  return (
    <div className="mm-prompt-display">
      <pre className="mm-prompt-content" tabIndex={0} aria-label="Generated Prompt">
        <code>{prompt}</code>
      </pre>
      <button className="mm-copy-btn" onClick={handleCopy} aria-label="Copy prompt to clipboard">Copy</button>
    </div>
  );
};
