// Server-side cache middleware for TTS audio (Node.js/Express style)
// Phase 1: Performance & Cost
import type { NextApiRequest, NextApiResponse } from 'next';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || '');
const CACHE_TTL = 60 * 60 * 24; // 24 hours

export default async function ttsCacheMiddleware(req: NextApiRequest, res: NextApiResponse, next: () => void) {
  if (req.method !== 'POST') return next();
  const { text, voice, model, speed } = req.body;
  const hash = Buffer.from(`${text}:${voice}:${model}:${speed}`).toString('base64');
  const cached = await redis.get(hash);
  if (cached) {
    res.setHeader('X-TTS-Cache', 'HIT');
    res.setHeader('Content-Type', 'audio/mpeg');
    res.send(Buffer.from(cached, 'base64'));
    return;
  }
  // On miss, let the request continue, and cache in the handler
  res.locals = res.locals || {};
  res.locals.ttsCacheKey = hash;
  next();
}

export async function cacheTTSResult(hash: string, audioBuffer: Buffer) {
  await redis.set(hash, audioBuffer.toString('base64'), 'EX', CACHE_TTL);
}
