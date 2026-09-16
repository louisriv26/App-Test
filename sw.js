/* Luisa Piccarreta PWA — Service Worker v2.3 R5
   Stage 8 CACHE-SCOPE-COLL-01:
   - index.html / navigation shell → network-first with HTTP-cache bypass, cache fallback
   - corpus.json → network-first with HTTP-cache bypass, cache fallback
   - local static assets → cache-first
   - all UI fonts and Tabler icons are local, exact-version assets precached in the scoped shell
   - Cache Storage ownership is bound to the exact Service Worker registration scope
   - ambiguous legacy unscoped caches are intentionally not globally deleted on first transition
   - a failed install fails closed, leaving the previously active worker/app intact
*/
function scopeFingerprint(scope) {
  let h = 2166136261;
  const text = String(scope || '');
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const SCOPE_FINGERPRINT = scopeFingerprint(self.registration.scope);
const APP_CACHE_PREFIX = `luisa-letters-${SCOPE_FINGERPRINT}-`;
const SHELL_CACHE = `${APP_CACHE_PREFIX}shell-v2.3-r5`;
const CORPUS_CACHE = `${APP_CACHE_PREFIX}corpus-v2.3-r5`;
const CANONICAL_SHELL_URL = './index.html';
const CORPUS_URL = './corpus.json';

const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-60.png',
  './icons/icon-120.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-16.png',
  './icons/favicon-32.png',
  './icons/favicon.ico',
  './fonts/crimson-text-400.woff2',
  './fonts/crimson-text-600.woff2',
  './fonts/crimson-text-400-italic.woff2',
  './fonts/im-fell-english-400.woff2',
  './fonts/im-fell-english-400-italic.woff2',
  './fonts/OFL-Crimson-Text.txt',
  './fonts/OFL-IM-Fell-English.txt',
  './vendor/tabler/tabler-sprite.svg',
  './vendor/tabler/LICENSE.txt',
];

function isOwnedCacheName(name) {
  return name.startsWith(APP_CACHE_PREFIX);
}

async function freshFetch(urlOrRequest) {
  const request = typeof urlOrRequest === 'string'
    ? new Request(urlOrRequest, {cache:'reload'})
    : new Request(urlOrRequest, {cache:'reload'});
  const response = await fetch(request);
  if (!response || !response.ok) throw new Error('fresh_fetch_failed:' + request.url + ':' + (response && response.status));
  return response;
}

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const shellCache = await caches.open(SHELL_CACHE);
    const corpusCache = await caches.open(CORPUS_CACHE);
    // cache:'reload' prevents stale browser HTTP-cache bytes from seeding a new release cache.
    for (const url of APP_SHELL) {
      const response = await freshFetch(url);
      await shellCache.put(url, response.clone());
    }
    // Precache the protected corpus in its own cache before install can succeed. This closes
    // the activation/offline gap where the old corpus cache could be removed before the new
    // page had a chance to fetch corpus.json under the new worker.
    const corpusResponse = await freshFetch(CORPUS_URL);
    await corpusCache.put(CORPUS_URL, corpusResponse.clone());
    // Deliberately do not skipWaiting here. The running app remains in control until explicit activation.
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter(name => isOwnedCacheName(name) && name !== SHELL_CACHE && name !== CORPUS_CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET') return;

  if (url.origin === self.location.origin && url.pathname.endsWith('corpus.json')) {
    event.respondWith(networkFirstCorpus(event.request));
    return;
  }


  if (url.origin === self.location.origin && (url.pathname === '/' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/'))) {
    event.respondWith(networkFirstShell(event.request));
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(event.request));
  }
});

async function networkFirstCorpus(request) {
  let networkResponse = null;
  try {
    const response = await fetch(request, {cache:'no-store'});
    if (response.ok) {
      const cache = await caches.open(CORPUS_CACHE);
      await cache.put(request, response.clone());
      return response;
    }
    networkResponse = response;
  } catch (e) {
    // Fall through to the last known-good cached corpus.
  }
  const cache = await caches.open(CORPUS_CACHE);
  const cached = await cache.match(request) || await cache.match(CORPUS_URL);
  if (cached) return cached;
  if (networkResponse) return networkResponse;
  return new Response(JSON.stringify({error:'corpus_unavailable',letters:[]}), {status:503,headers:{'Content-Type':'application/json'}});
}

async function networkFirstShell(request) {
  let networkResponse = null;
  try {
    const response = await fetch(request, {cache:'no-store'});
    if (response.ok) {
      const cache = await caches.open(SHELL_CACHE);
      // Store every successful navigation response under one canonical shell key instead of
      // proliferating one cache entry per deep-link query string.
      await cache.put(CANONICAL_SHELL_URL, response.clone());
      return response;
    }
    networkResponse = response;
  } catch (e) {
    // Fall through to the last known-good cached shell.
  }
  // A deep link such as ?letter=... or a manifest shortcut must still open from the cached
  // canonical shell when the network is unreachable or returns a non-OK HTTP response.
  const cache = await caches.open(SHELL_CACHE);
  const cached = await cache.match(request) || await cache.match(CANONICAL_SHELL_URL) || await cache.match('./');
  if (cached) return cached;
  if (networkResponse) return networkResponse;
  return new Response('Offline', {status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
}

async function cacheFirst(request) {
  const cache = await caches.open(SHELL_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put(request, response.clone());
    return response;
  } catch (e) {
    return new Response('Offline — ressource non disponible', {status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
  }
}

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
