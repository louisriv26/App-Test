/* Stage 6K— evidence integrity and stale-reference cleanup — prototype-95
   No app-shell cache. Network-first only. This file exists only to replace old cached service workers safely. */
const CACHE_NAME = 'luisa-24h-prototype-95';
self.addEventListener('install', event => { self.skipWaiting(); });
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('luisa-24h-')).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('message', event => { if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting(); });
self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  event.respondWith(fetch(req, { cache: 'no-store' }).catch(() => new Response('', { status: 503, statusText: 'Offline: network required for Stage 6K— evidence integrity and stale-reference cleanup recovery build' })));
});
