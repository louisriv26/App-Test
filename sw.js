/* Stage 5C-R5 service worker — prototype-74 */
const CACHE_NAME = 'luisa-24h-prototype-74';
const APP_SHELL = [
  './',
  './index.html',
  './luisa_24_heures.html',
  './manifest.json',
  './version.json',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME && key.startsWith('luisa-24h-')).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('/version.json')) {
    event.respondWith(fetch(req).then(resp => {
      if (resp && resp.ok) {
        const copy = resp.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
      }
      return resp;
    }).catch(() => caches.match(req).then(cached => cached || caches.match('./version.json'))));
    return;
  }
  event.respondWith(caches.match(req).then(cached => cached || fetch(req).then(resp => {
    if (resp && resp.ok && (url.pathname.endsWith('/index.html') || url.pathname.endsWith('/luisa_24_heures.html') || url.pathname.endsWith('/manifest.json'))) {
      const copy = resp.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
    }
    return resp;
  }).catch(() => caches.match('./index.html').then(fallback => fallback || caches.match('./luisa_24_heures.html')))));
});
