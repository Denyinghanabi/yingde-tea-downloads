const RELEASE = 'https://github.com/Denyinghanabi/yingde-tea-downloads/releases/download/v1.0.2/';
const LARGE_FILES = {
  '/downloads/yingde-video.mp4': ['yingde-video.mp4', 'video/mp4', '英德红茶视频.mp4'],
  '/downloads/yingde-complete.zip': ['yingde-complete.zip', 'application/zip', '英德红茶_作品合集.zip'],
};

export default {
  async fetch(request, env) {
    const file = LARGE_FILES[new URL(request.url).pathname];
    if (!file) return env.ASSETS.fetch(request);
    if (!['GET', 'HEAD'].includes(request.method)) {
      return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET, HEAD' } });
    }
    const headers = new Headers();
    for (const name of ['Range', 'If-Range', 'If-None-Match', 'If-Modified-Since']) {
      if (request.headers.has(name)) headers.set(name, request.headers.get(name));
    }
    let upstream;
    try {
      upstream = await fetch(RELEASE + file[0], { method: request.method, headers, redirect: 'follow' });
    } catch {
      return new Response('下载暂时不可用，请稍后重试。', { status: 502, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' } });
    }
    if (!upstream.ok && ![304, 416].includes(upstream.status)) {
      return new Response('下载暂时不可用，请稍后重试。', { status: 502, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' } });
    }
    const responseHeaders = new Headers();
    for (const name of ['Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag', 'Last-Modified']) {
      if (upstream.headers.has(name)) responseHeaders.set(name, upstream.headers.get(name));
    }
    responseHeaders.set('Content-Type', file[1]);
    responseHeaders.set('Content-Disposition', `attachment; filename="${file[0]}"; filename*=UTF-8''${encodeURIComponent(file[2])}`);
    responseHeaders.set('Cache-Control', upstream.ok ? 'public, max-age=3600' : 'no-store');
    responseHeaders.set('X-Content-Type-Options', 'nosniff');
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  },
};
