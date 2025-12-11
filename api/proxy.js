// Vercel API route to proxy requests to the backend
export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // Determine the backend URL based on environment
    // Use environment variable or default to localhost
    const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

    // Get the API endpoint from the URL path
    // The path will be everything after /api/proxy
    const { path } = req.query;
    const endpoint = path ? `/${Array.isArray(path) ? path.join('/') : path}` : '/';

    // Build the target URL
    const targetUrl = `${BACKEND_URL}${endpoint}`;

    // Prepare the request options
    const options = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers,
      },
    };

    // Remove headers that should not be forwarded
    delete options.headers.host;
    delete options.headers['content-length'];

    // Include body for POST/PUT requests
    if (req.body && (req.method === 'POST' || req.method === 'PUT')) {
      options.body = JSON.stringify(req.body);
    }

    // Make the request to the backend
    const backendRes = await fetch(targetUrl, options);

    // Get response data
    const data = await backendRes.json();

    // Return the response from the backend
    res.status(backendRes.status).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Proxy error', details: error.message });
  }
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};