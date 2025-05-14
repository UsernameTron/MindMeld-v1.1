import type { NextApiRequest, NextApiResponse } from 'next';

// External API base URLs - these should be set in environment variables
const API_ENDPOINTS: Record<string, string> = {
  librechat: process.env.LIBRECHAT_API_URL || 'https://librechat.example.com/api',
  // Add other external APIs as needed
};

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
    const pathSegments = req.query.path as string[];
    
    if (!pathSegments || pathSegments.length < 2) {
      return res.status(400).json({ 
        message: 'Invalid proxy request. Use /api/proxy/{service}/{endpoint}' 
      });
    }

    // First segment is the service name (e.g., 'librechat')
    const service = pathSegments[0];
    // Rest of the segments are the API path
    const apiPath = pathSegments.slice(1).join('/');

    // Get the base URL for the requested service
    const baseUrl = API_ENDPOINTS[service];
    if (!baseUrl) {
      return res.status(400).json({ message: `Unsupported service: ${service}` });
    }

    // Create full API URL
    const apiUrl = `${baseUrl}/${apiPath}`;

    console.log(`Proxying request to: ${apiUrl}`);

    // Forward the request to the external API
    const response = await fetch(apiUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization if available but don't include cookies
        ...(req.headers.authorization ? { 'Authorization': req.headers.authorization as string } : {})
      },
      // Only include body for non-GET requests
      body: req.method !== 'GET' && req.body ? JSON.stringify(req.body) : undefined,
    });

    // Get the response data
    let data: any;
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      data = await response.json().catch(() => null);
    } else {
      data = await response.text().catch(() => null);
    }

    // Forward the status code and data back to the client
    if (contentType?.includes('application/json')) {
      res.status(response.status).json(data || { message: 'No data returned from API' });
    } else {
      res.status(response.status).send(data || 'No data returned from API');
    }
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ message: 'Failed to communicate with external API' });
  }
}