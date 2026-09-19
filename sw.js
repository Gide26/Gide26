/* Circadia service worker — offline shell + reminder notifications */
const CACHE = "circadia-v3";
const ASSETS = [
  "./",
  "./index.html",
  "./css/app.css",
  "./js/db.js",
  "./js/reminders.js",
  "./js/app.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  const isAppShell =
    url.origin === self.location.origin ||
    url.hostname === "fonts.googleapis.com" ||
    url.hostname === "fonts.gstatic.com";

  if (!isAppShell) return;

  event.respondWith(
    caches.match(req).then((cached) => {
      const fetched = fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || fetched;
    })
  );
});

self.addEventListener("message", (event) => {
  const data = event.data || {};
  if (data.type === "notify") {
    event.waitUntil(
      self.registration.showNotification(data.title || "Circadia", {
        body: data.body || "",
        icon: "./icons/icon-192.png",
        badge: "./icons/icon-192.png",
        tag: data.tag || "circadia-reminder",
        renotify: true,
        vibrate: [180, 80, 180, 80, 240],
        data: { url: "./index.html", eventId: data.eventId || null },
        requireInteraction: true,
        silent: false,
      })
    );
  }

  if (data.type === "schedule" && data.timestamp) {
    event.waitUntil(scheduleTriggeredNotification(data));
  }

  if (data.type === "cancel" && data.tag) {
    event.waitUntil(
      self.registration.getNotifications({ tag: data.tag }).then((list) => {
        list.forEach((n) => n.close());
      })
    );
  }
});

async function scheduleTriggeredNotification(data) {
  try {
    const Trigger = self.TimestampTrigger || globalThis.TimestampTrigger;
    if (!Trigger) return;
    await self.registration.showNotification(data.title || "Circadia", {
      body: data.body || "",
      icon: "./icons/icon-192.png",
      badge: "./icons/icon-192.png",
      tag: data.tag || `circadia-${data.timestamp}`,
      showTrigger: new Trigger(data.timestamp),
      data: { url: "./index.html", eventId: data.eventId || null },
      requireInteraction: true,
    });
  } catch (err) {
    /* TimestampTrigger is experimental — in-app engine still fires. */
  }
}

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || "./index.html";
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ("focus" in client) {
          client.postMessage({ type: "notification-click", eventId: event.notification.data?.eventId });
          return client.focus();
        }
      }
      if (self.clients.openWindow) return self.clients.openWindow(target);
    })
  );
});

self.addEventListener("periodicsync", (event) => {
  if (event.tag === "circadia-reminders") {
    event.waitUntil(nudgeClients());
  }
});

async function nudgeClients() {
  const clients = await self.clients.matchAll({ type: "window" });
  clients.forEach((c) => c.postMessage({ type: "check-reminders" }));
}
