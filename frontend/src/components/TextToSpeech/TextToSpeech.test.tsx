import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TextToSpeech } from './TextToSpeech';
import { vi } from 'vitest';

vi.mock('../../hooks/useServices', () => {
  return {
    useServices: () => ({
      ttsService: mockTtsService
    })
  };
});

const mockTtsService = {
  convertTextToSpeech: vi.fn()
};

beforeAll(() => {
  Object.defineProperty(window.HTMLMediaElement.prototype, 'play', {
    configurable: true,
    value: vi.fn().mockResolvedValue(undefined),
  });
});

describe('<TextToSpeech />', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders input and controls', () => {
    render(<TextToSpeech />);
    expect(screen.getByPlaceholderText(/enter text/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/voice/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/model/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/speed/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /convert/i })).toBeInTheDocument();
  });

  it('updates textarea value', () => {
    render(<TextToSpeech />);
    const textarea = screen.getByPlaceholderText(/enter text/i);
    fireEvent.change(textarea, { target: { value: 'Test speech' } });
    expect((textarea as HTMLTextAreaElement).value).toBe('Test speech');
  });

  it('calls ttsService and displays audio on success', async () => {
    mockTtsService.convertTextToSpeech.mockResolvedValue({
      audioUrl: '/audio/test.mp3',
      duration: 1.23,
      characterCount: 11
    });
    render(<TextToSpeech />);
    fireEvent.change(screen.getByPlaceholderText(/enter text/i), { target: { value: 'Test speech' } });
    fireEvent.click(screen.getByRole('button', { name: /convert/i }));
    await waitFor(() => expect(mockTtsService.convertTextToSpeech).toHaveBeenCalled());
    expect(await screen.findByTestId('tts-audio')).toBeInTheDocument();
    expect(screen.getByText(/duration/i)).toHaveTextContent('1.23');
    expect(screen.getByText(/characters/i)).toHaveTextContent('11');
    expect(screen.getByRole('link', { name: /download/i })).toHaveAttribute('href', '/audio/test.mp3');
  });

  it('shows error and recovers', async () => {
    mockTtsService.convertTextToSpeech.mockRejectedValue(new Error('TTS failed'));
    render(<TextToSpeech />);
    fireEvent.change(screen.getByPlaceholderText(/enter text/i), { target: { value: 'fail' } });
    fireEvent.click(screen.getByRole('button', { name: /convert/i }));
    expect(await screen.findByText(/tts failed/i)).toBeInTheDocument();
    // Try again with success
    mockTtsService.convertTextToSpeech.mockResolvedValue({
      audioUrl: '/audio/ok.mp3', duration: 2, characterCount: 2
    });
    fireEvent.change(screen.getByPlaceholderText(/enter text/i), { target: { value: 'ok' } });
    fireEvent.click(screen.getByRole('button', { name: /convert/i }));
    expect(await screen.findByTestId('tts-audio')).toBeInTheDocument();
  });

  it('calls onSpeechGenerated callback', async () => {
    const cb = vi.fn();
    mockTtsService.convertTextToSpeech.mockResolvedValue({
      audioUrl: '/audio/cb.mp3', duration: 1, characterCount: 2
    });
    render(<TextToSpeech onSpeechGenerated={cb} />);
    fireEvent.change(screen.getByPlaceholderText(/enter text/i), { target: { value: 'cb' } });
    fireEvent.click(screen.getByRole('button', { name: /convert/i }));
    await waitFor(() => expect(cb).toHaveBeenCalledWith({
      audioUrl: '/audio/cb.mp3', duration: 1, characterCount: 2
    }));
  });
});
