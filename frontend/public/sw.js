/* Service Worker — Drwintech Fleet (espace client PWA) */
const CACHE = "fleet-client-v1";
const APP_SHELL = ["/client"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first pour la navigation, fallback cache (offline léger).
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() => caches.match("/client"))
    );
  }
});

// --- Web Push (Phase C) ---
self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: "Alerte", body: event.data ? event.data.text() : "" };
  }
  const title = data.title || "Drwintech Fleet";
  event.waitUntil(
    self.registration.showNotification(title, {
      body: data.body || "",
      icon: "/icon.svg",
      badge: "/icon.svg",
      data: data,
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow("/client/alertes"));
});
