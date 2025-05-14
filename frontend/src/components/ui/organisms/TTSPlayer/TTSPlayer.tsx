import React, { useState, useRef } from 'react';
import { useAuth } from '../../../../context/AuthContext';

const VOICES = [
  { value: 'alloy', label: 'Alloy' },
  { value: 'echo', label: 'Echo' },
  { value: 'fable', label: 'Fable' },
  { value: 'onyx', label: 'Onyx' },
  { value: 'nova', label: 'Nova' },
  { value: 'shimmer', label: 'Shimmer' },
];

export default function TTSPlayer() {
  const { isAuthenticated } = useAuth();
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('alloy');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleGenerate = async () => {
    setError(null);
    setAudioUrl(null);
    if (!text.trim()) {
      setError('Text is required.');
      return;
    }
    if (text.length > 4096) {
      setError('Text must be 4096 characters or less.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/tts/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.error || 'Failed to generate audio.');
        setLoading(false);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    } catch (e: any) {
      setError(e.message || 'Network error.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!audioUrl) return;
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = 'tts-audio.mp3';
    a.click();
  };

  if (!isAuthenticated) {
    return <div className="tts-player-locked">Please log in to use Text-to-Speech.</div>;
  }

  return (
    <div className="tts-player">
      <label>
        Voice:
        <select value={voice} onChange={e => setVoice(e.target.value)} disabled={loading}>
          {VOICES.map(v => (
            <option key={v.value} value={v.value}>{v.label}</option>
          ))}
        </select>
      </label>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        maxLength={4096}
        placeholder="Enter text (max 4096 chars)"
        disabled={loading}
        rows={4}
        style={{ width: '100%' }}
      />
      <button onClick={handleGenerate} disabled={loading || !text.trim()}>
        {loading ? 'Generating...' : 'Generate Audio'}
      </button>
      {audioUrl && (
        <div className="tts-audio-controls">
          <audio ref={audioRef} src={audioUrl} controls autoPlay />
          <button onClick={handleDownload}>Download MP3</button>
        </div>
      )}
      {error && <div className="tts-error" style={{ color: 'red' }}>{error}</div>}
    </div>
  );
}
