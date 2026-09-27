/* Kill-switch service worker.
 *
 * An app previously published at this address ("Circadia") registered a
 * cache-first service worker at ./sw.js, so browsers that visited it keep
 * showing the old cached pages. Browsers re-fetch sw.js on each visit; this
 * file replaces the old worker, wipes its caches, unregisters itself and
 * reloads any open tabs so the current site appears. It leaves nothing behind.
 */
self.addEventListener("install", function () {
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil((async function () {
    try {
      var keys = await caches.keys();
      await Promise.all(keys.map(function (k) { return caches.delete(k); }));
    } catch (e) { /* ignore */ }
    try { await self.clients.claim(); } catch (e) { /* ignore */ }
    try { await self.registration.unregister(); } catch (e) { /* ignore */ }
    try {
      var clients = await self.clients.matchAll({ type: "window" });
      clients.forEach(function (c) {
        if ("navigate" in c) c.navigate(c.url);
      });
    } catch (e) { /* ignore */ }
  })());
});
