/* Service worker: caches the app shell only.
 * Business data is NEVER cached — every /api/ request goes to the server,
 * so two devices can never disagree about what has been sold.
 * Bump VERSION whenever the front-end changes to force a refresh. */

const VERSION = 'bakery-v1.1.0';

const SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icon.svg',
  '/css/styles.css',
  '/js/app.js',
  '/js/api.js',
  '/js/format.js',
  '/js/ui.js',
  '/js/charts.js',
  '/js/store.js',
  '/js/offline.js',
  '/js/router.js',
  '/js/views/login.js',
  '/js/views/dashboard.js',
  '/js/views/pos.js',
  '/js/views/sales.js',
  '/js/views/products.js',
  '/js/views/inventory.js',
  '/js/views/expenses.js',
  '/js/views/customers.js',
  '/js/views/reports.js',
  '/js/views/settings.js',
  '/js/views/more.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(VERSION)
      .then((cache) => Promise.allSettled(SHELL.map((url) => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/api/')) return; // always live

  // Navigations: network first so updates arrive, cache when offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put('/index.html', copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match('/index.html').then((hit) => hit || Response.error()))
    );
    return;
  }

  // Static assets: cache first, refresh in the background.
  event.respondWith(
    caches.match(req).then((hit) => {
      const network = fetch(req).then((res) => {
        if (res && res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      }).catch(() => hit);
      return hit || network;
    })
  );
});
