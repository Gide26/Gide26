/**
 * HTTP server: serves the API and the static front-end from one port, so
 * the app works identically on a computer and on a phone with no CORS
 * configuration and no separate build step.
 */
import { createServer } from 'node:http';
import { createReadStream, existsSync, statSync, readFileSync } from 'node:fs';
import { join, normalize, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

import { db, DB_PATH, DATA_DIR, getSetting, isEmpty, tableCounts } from './db.js';
import { createRouter } from './router.js';
import { registerApiRoutes } from './api.js';
import { registerReportRoutes } from './reports.js';
import { pruneSessions } from './auth.js';
import { str } from './util.js';
import { seedDemo } from './seed.js';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const PUBLIC_DIR = resolve(HERE, '..', 'public');
const HOST = process.env.HOST || '0.0.0.0';
const PORT = Number(process.env.PORT || 3000);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
};

const router = createRouter();
registerApiRoutes(router);
registerReportRoutes(router);

/* ------------------------------------------------------------------ *
 * Security headers
 * ------------------------------------------------------------------ */
const SECURITY_HEADERS = {
  'x-content-type-options': 'nosniff',
  'x-frame-options': 'DENY',
  'referrer-policy': 'same-origin',
  'permissions-policy': 'geolocation=(), camera=(), microphone=()',
  'content-security-policy': [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "manifest-src 'self'",
    "worker-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; '),
};

function send(res, status, headers, body) {
  const isHead = headers.__head;
  delete headers.__head;
  const payload = body == null ? '' : body;
  const length = typeof payload === 'string' ? Buffer.byteLength(payload) : payload?.length ?? 0;
  res.writeHead(status, { ...SECURITY_HEADERS, 'content-length': length, ...headers });
  if (isHead || length === 0) return res.end();
  res.end(payload);
}

const json = (res, status, data, extra = {}) =>
  send(res, status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
    JSON.stringify(data));

/* ------------------------------------------------------------------ *
 * Static files
 * ------------------------------------------------------------------ */

function etagFor(st) {
  return createHash('sha1').update(`${st.size}:${Math.floor(st.mtimeMs)}`).digest('base64url').slice(0, 20);
}

function serveStatic(req, res, pathname) {
  let rel = decodeURIComponent(pathname);
  if (rel.endsWith('/')) rel += 'index.html';
  const filePath = join(PUBLIC_DIR, normalize(rel).replace(/^(\.\.[/\\])+/, ''));

  // Contain every request inside public/
  if (!filePath.startsWith(PUBLIC_DIR)) return send(res, 403, {}, 'Forbidden');
  if (!existsSync(filePath) || !statSync(filePath).isFile()) return null;

  const st = statSync(filePath);
  const etag = `"${etagFor(st)}"`;
  if (str(req.headers['if-none-match']) === etag) {
    return send(res, 304, { etag, 'cache-control': 'no-cache' }, '');
  }

  const type = MIME[extname(filePath).toLowerCase()] || 'application/octet-stream';
  const headers = {
    'content-type': type,
    etag,
    // Revalidate every time: no stale front-end after an update.
    'cache-control': 'no-cache',
    ...(type.endsWith('application/octet-stream') ? { 'content-disposition': 'attachment' } : {}),
  };
  if (req.method === 'HEAD') return send(res, 200, { ...headers, __head: true }, '');

  res.writeHead(200, { ...SECURITY_HEADERS, ...headers });
  const stream = createReadStream(filePath);
  stream.on('error', () => { try { res.destroy(); } catch { /* ignore */ } });
  stream.pipe(res);
  return true;
}

/* ------------------------------------------------------------------ *
 * Request handling
 * ------------------------------------------------------------------ */

const MANIFEST_PATH = join(PUBLIC_DIR, 'manifest.webmanifest');
let manifestBase = null;

/**
 * The web manifest, with the business's own name in it.
 *
 * An installed PWA takes its home-screen label from here, so serving a static
 * "Bakery Tracker" would put a name on the phone that has nothing to do with the
 * bakery using it. Generating it from settings means renaming the business in
 * Settings is what every device installs as from then on.
 *
 * `short_name` is the one that actually fits under an icon, so it is derived
 * rather than fixed: the first word of the business name, capped.
 */
function buildManifest() {
  if (manifestBase === null) {
    try {
      manifestBase = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'));
    } catch {
      manifestBase = { name: 'Bakery Tracker', short_name: 'Bakery', id: '/', start_url: '/',
        scope: '/', display: 'standalone', background_color: '#FBF7F2', theme_color: '#241A13',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ] };
    }
  }
  const name = String(getSetting('business_name', '') || '').trim() || String(manifestBase.name || 'Bakery Tracker');
  // The home-screen label has to be short, but a single word can be useless:
  // "Mama G's Bakery House" truncated naively would read "Mama". Take as many
  // leading words as fit, so it becomes "Mama G's" instead.
  const words = name.split(/\s+/);
  let short = words[0] || name;
  for (const w of words.slice(1)) {
    if (`${short} ${w}`.length > 14) break;
    short = `${short} ${w}`;
  }
  return JSON.stringify({ ...manifestBase, name, short_name: short });
}

const server = createServer(async (req, res) => {
  const started = Date.now();
  let url;
  try {
    url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  } catch {
    return send(res, 400, {}, 'Bad request');
  }

  try {
    if (url.pathname.startsWith('/api/')) {
      const result = await router.handle(req, url);
      if (result) {
        send(res, result.status, result.headers, result.body);
        return log(req, url, result.status, started);
      }
      return send(res, 404, { 'content-type': 'application/json; charset=utf-8' },
        JSON.stringify({ error: `No such endpoint: ${req.method} ${url.pathname}`, status: 404 }));
    }

    // Served before the static handler so the generated version wins over the
    // file on disk. Never cached: a rename should show up on the next launch.
    if (url.pathname === '/manifest.webmanifest') {
      send(res, 200, { 'content-type': MIME['.webmanifest'], 'cache-control': 'no-cache' }, buildManifest());
      return log(req, url, 200, started);
    }

    // Everything else is the front-end.
    const served = serveStatic(req, res, url.pathname);
    if (served !== null) return;

    // A request that names a file which does not exist is a genuine 404.
    // Only extension-less paths are client-side routes that deserve the SPA
    // shell — this stops /server/db.js or /data/bakery.sqlite answering 200.
    // Any dot-prefixed segment (/.git/config, /.env, /.gitignore) also 404s.
    const hasDotSegment = url.pathname.split('/').some((s) => s.startsWith('.'));
    if (extname(url.pathname) || hasDotSegment) return send(res, 404, {}, 'Not found');

    // Unknown path: hand back the app shell so client-side routing works.
    if (existsSync(join(PUBLIC_DIR, 'index.html'))) {
      res.writeHead(200, { ...SECURITY_HEADERS, 'content-type': MIME['.html'], 'cache-control': 'no-cache' });
      return createReadStream(join(PUBLIC_DIR, 'index.html')).pipe(res);
    }
    send(res, 404, {}, 'Not found');
  } catch (err) {
    console.error('[fatal request error]', err);
    if (!res.headersSent) json(res, 500, { error: 'Internal server error', status: 500 });
    else try { res.end(); } catch { /* ignore */ }
  }
});

function log(req, url, status, started) {
  const ms = Date.now() - started;
  if (url.pathname === '/api/health') return;
  console.log(`${req.method} ${url.pathname}${url.search || ''} -> ${status} (${ms}ms)`);
}

/* ------------------------------------------------------------------ *
 * Boot
 * ------------------------------------------------------------------ */

const banner = (title, lines) => {
  const width = Math.max(title.length + 4, ...lines.map((l) => l.length + 4), 56);
  const bar = '─'.repeat(width);
  console.log(`\n┌${bar}┐`);
  console.log(`│  ${title.padEnd(width - 4)}  │`);
  console.log(`├${bar}┤`);
  for (const l of lines) console.log(`│  ${l.padEnd(width - 4)}  │`);
  console.log(`└${bar}┘\n`);
};

function startup() {
  // Auto-seed the demo dataset unless explicitly disabled.
  const wantDemo = (process.env.BAKERY_SEED || 'demo').toLowerCase();
  if (isEmpty()) {
    if (wantDemo === 'demo') {
      const out = seedDemo({ force: false });
      if (!out.skipped) {
        banner('Bakery Tracker — demo data loaded', [
          `Sales: ${out.sales}   Products: ${out.products}   Ingredients: ${out.ingredients}`,
          `${out.days} days of trading history so the reports are populated.`,
          '',
          '  Owner  →  phone 079000000   password changeme',
          '  Staff  →  phone 079111111   password staff123',
          '',
          'Change both passwords in Settings before real use.',
        ]);
      }
    } else {
      banner('Bakery Tracker — empty database', [
        'Open the app and choose "Set up my business" to create',
        'your owner account, or run:',
        '',
        '  npm run seed-demo',
      ]);
    }
  }

  const counts = tableCounts();
  server.listen(PORT, HOST, () => {
    const business = getSetting('business_name', 'Bakery');
    banner(`${business} — Bakery Tracker`, [
      `Listening on   http://${HOST}:${PORT}`,
      `Database       ${DB_PATH}`,
      `Data folder    ${DATA_DIR}`,
      `Timezone       ${getSetting('timezone')}`,
      `Currency       ${getSetting('currency_symbol')} ${getSetting('currency_code')}`,
      '',
      `Users ${counts.users} · Products ${counts.products} · Sales ${counts.sales} · Expenses ${counts.expenses}`,
      '',
      'Press Ctrl+C to stop.',
    ]);
  });

  // Housekeeping: clear expired sessions hourly.
  const timer = setInterval(() => {
    const n = pruneSessions();
    if (n) console.log(`[housekeeping] removed ${n} expired session(s)`);
  }, 3600_000);
  timer.unref();
}

function shutdown(signal) {
  console.log(`\n[${signal}] shutting down…`);
  server.close(() => {
    try { db.close(); } catch { /* ignore */ }
    process.exit(0);
  });
  setTimeout(() => process.exit(0), 3000).unref();
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('uncaughtException', (err) => {
  console.error('[uncaughtException]', err);
});
process.on('unhandledRejection', (err) => {
  console.error('[unhandledRejection]', err);
});

startup();
