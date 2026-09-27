/**
 * Minimal dependency-free router: pattern matching with :params, JSON body
 * parsing with a size cap, auth context injection, and error normalisation.
 */
import { HttpError, str, unauthorized } from './util.js';
import { parseCookies, userFromToken, COOKIE_NAME } from './auth.js';

const MAX_BODY_BYTES = 1_000_000; // 1 MB — far more than any form or cart needs

function compile(pattern) {
  const names = [];
  const rx = new RegExp(
    '^' + pattern.replace(/\/:[A-Za-z_][A-Za-z0-9_]*/g, (m) => {
      names.push(m.slice(2));
      return '/([^/]+)';
    }).replace(/\//g, '\\/') + '/?$'
  );
  return { rx, names };
}

export function createRouter() {
  const routes = [];

  function add(method, pattern, handler, opts = {}) {
    const { rx, names } = compile(pattern);
    routes.push({ method, pattern, rx, names, handler, owner: !!opts.owner });
  }

  const router = {
    get: (p, h, o) => add('GET', p, h, o),
    post: (p, h, o) => add('POST', p, h, o),
    put: (p, h, o) => add('PUT', p, h, o),
    patch: (p, h, o) => add('PATCH', p, h, o),
    delete: (p, h, o) => add('DELETE', p, h, o),
    routes,

    /** Returns { status, headers, body } or null when nothing matched. */
    async handle(req, url) {
      const method = req.method === 'HEAD' ? 'GET' : req.method;

      for (const r of routes) {
        if (r.method !== method) continue;
        const m = r.rx.exec(url.pathname);
        if (!m) continue;

        const params = {};
        r.names.forEach((n, i) => { params[n] = decodeURIComponent(m[i + 1]); });

        const cookies = parseCookies(req.headers.cookie || '');
        const token = cookies[COOKIE_NAME];
        let user = null;
        try { user = userFromToken(token); } catch { user = null; }

        if (r.owner && (!user || user.role !== 'owner')) {
          return errorResponse(user ? new HttpError(403, 'Only the owner can do that') : unauthorized(), url);
        }

        const ctx = {
          req,
          method,
          path: url.pathname,
          params,
          query: Object.fromEntries(url.searchParams.entries()),
          user,
          token,
          ip: clientIp(req),
          secure: isSecure(req, url),
          body: null,
        };

        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
          try {
            ctx.body = await readJson(req);
          } catch (err) {
            return errorResponse(new HttpError(400, `Bad request body: ${err.message}`), url);
          }
        }

        try {
          const out = await r.handler(ctx);
          return normalise(out);
        } catch (err) {
          return errorResponse(err, url);
        }
      }
      return null; // no route matched
    },
  };

  return router;
}

/** A handler may return plain data (sent as JSON) or a RawResponse. */
function normalise(out) {
  const headers = { 'cache-control': 'no-store' };
  if (out instanceof RawResponse) {
    return { status: out.status, headers: { ...headers, 'content-type': out.contentType, ...out.extra }, body: out.body };
  }
  return {
    status: 200,
    headers: { ...headers, 'content-type': 'application/json; charset=utf-8' },
    body: JSON.stringify(out ?? { ok: true }),
  };
}

class RawResponse {
  constructor(status, body, contentType, extraHeaders = {}) {
    this.status = status;
    this.body = body;
    this.contentType = contentType;
    this.extra = extraHeaders;
  }
}

export const raw = (status, body, contentType, extra) => new RawResponse(status, body, contentType, extra);

export const csv = (text, filename) =>
  new RawResponse(200, text, 'text/csv; charset=utf-8', {
    'content-disposition': `attachment; filename="${filename}"`,
  });

function errorResponse(err, url) {
  const status = err instanceof HttpError ? err.status : 500;
  if (status >= 500) {
    console.error(`[error] ${url.pathname}:`, err);
  }
  const payload = {
    error: status >= 500 ? 'Something went wrong on the server' : err.message,
    status,
    ...(err.details ? { details: err.details } : {}),
  };
  return {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
    body: JSON.stringify(payload),
  };
}

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new Error('payload too large');
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  const text = Buffer.concat(chunks).toString('utf8');
  const ct = str(req.headers['content-type']);
  if (ct && !ct.includes('application/json')) {
    throw new Error('expected JSON');
  }
  try {
    const parsed = JSON.parse(text);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    throw new Error('invalid JSON');
  }
}

export function clientIp(req) {
  const fwd = str(req.headers['x-forwarded-for']);
  if (fwd) return fwd.split(',')[0].trim();
  return req.socket?.remoteAddress || 'unknown';
}

/** Behind the Arena preview proxy the connection is TLS even though Node sees plain HTTP. */
export function isSecure(req, url) {
  return str(req.headers['x-forwarded-proto']) === 'https' || url.protocol === 'https:';
}
