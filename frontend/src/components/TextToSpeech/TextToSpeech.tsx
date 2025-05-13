import React, { useState, useRef } from 'react';
import { useServices } from '../../hooks/useServices';

export interface TextToSpeechProps {
  text?: string;
  onSpeechGenerated?: (result: any) => void;
  featureCategory?: string;
  className?: string;
}

export const TextToSpeech: React.FC<TextToSpeechProps> = ({
  text: initialText = '',
  onSpeechGenerated,
  featureCategory,
  className = '',
}) => {
  const { ttsService } = useServices();
  const [text, setText] = useState(initialText);
  const [voice, setVoice] = useState<'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer'>('nova');
  const [model, setModel] = useState<'tts-1' | 'tts-1-hd'>('tts-1');
  const [speed, setSpeed] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const res = await ttsService.convertTextToSpeech(text, { voice, model, speed });
      setResult(res);
      if (onSpeechGenerated) onSpeechGenerated(res);
      setTimeout(() => {
        audioRef.current?.play().catch(() => {});
      }, 100);
    } catch (err: any) {
      setError(err.message || 'TTS failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`bg-white rounded shadow p-4 ${className}`} data-feature={featureCategory}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="w-full border rounded p-2"
          rows={3}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Enter text to convert to speech..."
          required
        />
        <div className="flex gap-4 items-center">
          <label>
            Voice:
            <select value={voice} onChange={e => setVoice(e.target.value as any)} className="ml-2">
              <option value="alloy">Alloy</option>
              <option value="echo">Echo</option>
              <option value="fable">Fable</option>
              <option value="onyx">Onyx</option>
              <option value="nova">Nova</option>
              <option value="shimmer">Shimmer</option>
            </select>
          </label>
          <label>
            Model:
            <select value={model} onChange={e => setModel(e.target.value as any)} className="ml-2">
              <option value="tts-1">tts-1</option>
              <option value="tts-1-hd">tts-1-hd</option>
            </select>
          </label>
          <label>
            Speed:
            <input
              type="number"
              min={0.25}
              max={4.0}
              step={0.01}
              value={speed}
              onChange={e => setSpeed(Number(e.target.value))}
              className="ml-2 w-16"
            />
          </label>
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={loading || !text.trim()}
        >
          {loading ? 'Generating...' : 'Convert to Speech'}
        </button>
      </form>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      {result && (
        <div className="mt-4">
          <audio ref={audioRef} src={result.audioUrl} controls autoPlay style={{ width: '100%' }} data-testid="tts-audio" />
          <div className="flex gap-4 mt-2 items-center">
            <span>Duration: {result.duration.toFixed(2)}s</span>
            <span>Characters: {result.characterCount}</span>
            <a href={result.audioUrl} download="tts.mp3" className="text-blue-700 underline">Download MP3</a>
          </div>
        </div>
      )}
    </div>
  );
};
