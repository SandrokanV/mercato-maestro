/* ============================================================
   MERCATO MAESTRO · Service Worker
   Strategy:
   - HTML/JSON  → network-first  (fresca quando online, fallback cache)
   - Assets     → cache-first    (immagini, manifest, logo)
   ============================================================ */

const CACHE_VERSION = 'mm-cache-v1';
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/about.html',
  '/contact.html',
  '/privacy.html',
  '/cookies.html',
  '/manifest.json',
  '/logo.png',
  '/logo-192.png',
  '/apple-touch-icon.png',
  '/favicon-32.png',
  '/og-image.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(PRECACHE_URLS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Solo GET dello stesso dominio
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;

  const isDoc = req.destination === 'document' || url.pathname.endsWith('.html') || url.pathname === '/';
  const isData = url.pathname.endsWith('.json') || url.pathname.endsWith('.xml');

  if (isDoc || isData) {
    // Network-first
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match('/index.html')))
    );
  } else {
    // Cache-first
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
          }
          return res;
        }).catch(() => cached);
      })
    );
  }
});
