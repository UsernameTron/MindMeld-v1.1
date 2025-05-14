import type { NextApiRequest, NextApiResponse } from 'next';

// LibreChat API base URL - this should be set in environment variables
const LIBRECHAT_API_BASE = process.env.LIBRECHAT_API_URL || 'https://librechat.example.com/api';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow GET, POST, PUT, DELETE methods
  if (!['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'].includes(req.method || '')) {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    return res.status(200).end();
  }

  try {
    // Extract the path from the request
    const path = req.query.path as string || '';
    
    // Create full LibreChat API URL
    const apiUrl = `${LIBRECHAT_API_BASE}/${path}`;

    // Forward the request to LibreChat API
    const response = await fetch(apiUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization if available but don't include cookies
        ...(req.headers.authorization ? { 'Authorization': req.headers.authorization as string } : {})
      },
      body: req.method !== 'GET' && req.body ? JSON.stringify(req.body) : undefined,
    });

    // Get the response data
    const data = await response.json().catch(() => null);

    // Forward the status code and data back to the client
    res.status(response.status).json(data || { message: 'No data returned from API' });
  } catch (error) {
    console.error('LibreChat proxy error:', error);
    res.status(500).json({ message: 'Failed to communicate with LibreChat API' });
  }
}