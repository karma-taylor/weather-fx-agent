const STATIC_CACHE = "fx-static-v1";
const RUNTIME_CACHE = "fx-runtime-v1";

const STATIC_ASSETS = [
  "/",
  "/static/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Keep API POST calls online-only; frontend handles offline fallback logic.
  if (url.pathname.startsWith("/api/")) return;

  // Navigations: network first, fallback to cached "/".
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          const clone = resp.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put("/", clone)).catch(() => {});
          return resp;
        })
        .catch(() => caches.match("/") || caches.match(req))
    );
    return;
  }

  // Static/runtime assets: cache first, then network.
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((resp) => {
        if (resp && resp.status === 200 && resp.type === "basic") {
          const clone = resp.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put(req, clone)).catch(() => {});
        }
        return resp;
      });
    })
  );
});
