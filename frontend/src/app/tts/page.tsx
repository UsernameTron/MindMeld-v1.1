import React from 'react';
import { TextToSpeech } from '../../components/TextToSpeech';

export default function TTSPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Text to Speech</h1>
      <p className="mb-4">Convert text to natural-sounding speech using advanced AI models.</p>
      <TextToSpeech featureCategory="tts" />
    </div>
  );
}
