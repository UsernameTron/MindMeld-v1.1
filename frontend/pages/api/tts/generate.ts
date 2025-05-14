import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { text, voice = 'alloy' } = req.body || {};

  if (!text || typeof text !== 'string' || text.length === 0 || text.length > 4096) {
    return res.status(400).json({ error: 'Text is required and must be ≤ 4096 characters.' });
  }

  try {
    const audioResponse = await openai.audio.speech.create({
      model: 'tts-1',
      voice,
      input: text,
    });

    const buffer = Buffer.from(await audioResponse.arrayBuffer());
    // Optionally log buffer length for confirmation
    console.log('TTS buffer length:', buffer.length);

    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.status(200).send(buffer);
  } catch (err: any) {
    if (err?.status === 429) {
      return res.status(429).json({ error: 'Rate limit exceeded. Please try again later.' });
    }
    console.error('TTS API error:', err?.message || err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
