import React, { useState, useRef } from 'react';
import { cn } from '../../../frontend/src/utils/cn';
import { LoadingIndicator } from '../../../frontend/src/components/ui/molecules/LoadingIndicator';
import { ErrorDisplay } from '../../../frontend/src/components/ui/molecules/ErrorDisplay';

function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

interface Submission {
  url: string;
  result?: string;
  error?: string;
}

interface UrlInputFormProps {
  onSubmit?: (url: string) => void;
  loading?: boolean;
}

const UrlInputForm: React.FC<UrlInputFormProps> = ({ onSubmit, loading }) => {
  const [url, setUrl] = useState('');
  const [inputError, setInputError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setInputError(null);
    if (!isValidUrl(url)) {
      setInputError('Please enter a valid URL (must start with http:// or https://).');
      inputRef.current?.focus();
      return;
    }
    onSubmit?.(url);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 max-w-xl mx-auto p-4 bg-white rounded-lg shadow-md border border-gray-200"
      aria-label="URL Sentiment Analysis Form"
    >
      <div>
        <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 mb-1">
          Website URL
        </label>
        <input
          id="url-input"
          ref={inputRef}
          type="url"
          inputMode="url"
          autoComplete="url"
          required
          aria-required="true"
          aria-invalid={!!inputError}
          aria-describedby={inputError ? 'url-error' : undefined}
          className={cn(
            'block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition',
            inputError ? 'border-red-500' : 'border-gray-300'
          )}
          placeholder="https://example.com"
          value={url}
          onChange={e => setUrl(e.target.value)}
          disabled={loading}
        />
        {inputError && (
          <div id="url-error" className="mt-1 text-sm text-red-600" role="alert">
            {inputError}
          </div>
        )}
      </div>
      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition"
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? <LoadingIndicator size="sm" ariaLabel="Analyzing..." /> : 'Analyze Sentiment'}
      </button>
    </form>
  );
};

export default UrlInputForm;
