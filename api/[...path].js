export const config = {
  runtime: 'edge',
};

const BACKEND = 'https://orchestrated-agent.onrender.com';

export default async function handler(req) {
  const url = new URL(req.url);
  const targetUrl = BACKEND + url.pathname + url.search;

  const headers = new Headers(req.headers);
  headers.delete('host');

  const response = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined,
    duplex: 'half',
  });

  const responseHeaders = new Headers(response.headers);
  responseHeaders.set('Access-Control-Allow-Origin', '*');
  responseHeaders.set('Access-Control-Allow-Methods', '*');
  responseHeaders.set('Access-Control-Allow-Headers', '*');

  return new Response(response.body, {
    status: response.status,
    headers: responseHeaders,
  });
}
