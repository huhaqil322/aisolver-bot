export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const renderUrl = env.RENDER_APP_URL;

    if (!renderUrl) {
      return new Response('RENDER_APP_URL not configured', { status: 500 });
    }

    const targetUrl = renderUrl + url.pathname;
    const headers = new Headers(request.headers);
    headers.set('Host', new URL(renderUrl).host);

    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });

    return response;
  },
};
