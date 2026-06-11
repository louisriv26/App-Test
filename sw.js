/* Stage 6N — non-highlighting PWA/offline/update hardening — prototype-98 */
const CACHE_NAME = 'luisa-24h-prototype-98';
const CACHE_PREFIX = 'luisa-24h-';
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

async function cacheAppShell() {
  const cache = await caches.open(CACHE_NAME);
  await cache.addAll(APP_SHELL.map(url => new Request(url, { cache: 'reload' })));
}

self.addEventListener('install', event => {
  event.waitUntil(cacheAppShell().then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys
        .filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
        .map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

async function putOkResponse(request, response) {
  if (response && response.ok) {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request, fallbackUrls) {
  try {
    const response = await fetch(request, { cache: 'no-store' });
    return await putOkResponse(request, response);
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) return cached;
    for (const url of fallbackUrls || []) {
      const fallback = await caches.match(url);
      if (fallback) return fallback;
    }
    throw error;
  }
}

async function cacheFirst(request, fallbackUrls) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    return await putOkResponse(request, response);
  } catch (error) {
    for (const url of fallbackUrls || []) {
      const fallback = await caches.match(url);
      if (fallback) return fallback;
    }
    throw error;
  }
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.endsWith('/version.json')) {
    event.respondWith(networkFirst(req, ['./version.json']));
    return;
  }

  if (req.mode === 'navigate' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/luisa_24_heures.html')) {
    event.respondWith(networkFirst(req, ['./index.html', './luisa_24_heures.html']));
    return;
  }

  event.respondWith(cacheFirst(req, ['./index.html', './luisa_24_heures.html']));
});
