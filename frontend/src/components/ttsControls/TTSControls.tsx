// Shared TTS playback controls for MindMeld
// Phase 2: Accessibility & Integration
import React from 'react';

interface TTSControlsProps {
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onVolumeChange: (v: number) => void;
  volume: number;
  ariaLabel?: string;
}

export const TTSControls: React.FC<TTSControlsProps> = ({
  isPlaying,
  onPlay,
  onPause,
  onStop,
  onVolumeChange,
  volume,
  ariaLabel = 'Text to speech controls',
}) => (
  <div className="tts-controls" role="group" aria-label={ariaLabel}>
    <button
      aria-label={isPlaying ? 'Pause speech' : 'Play speech'}
      onClick={isPlaying ? onPause : onPlay}
      tabIndex={0}
    >
      {isPlaying ? '⏸️' : '▶️'}
    </button>
    <button aria-label="Stop speech" onClick={onStop} tabIndex={0}>⏹️</button>
    <label htmlFor="tts-volume" className="sr-only">Volume</label>
    <input
      id="tts-volume"
      type="range"
      min={0}
      max={1}
      step={0.01}
      value={volume}
      onChange={e => onVolumeChange(Number(e.target.value))}
      aria-valuenow={volume}
      aria-label="TTS volume"
      tabIndex={0}
    />
  </div>
);
