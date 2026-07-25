/* v101.24 */
const CACHE_NAME = 'luisa-24h-v101-24';
const CACHE_PREFIX = 'luisa-24h-';
const ASSETS = ['./','./index.html','./luisa_24_heures.html','./manifest.json','./icon-180.png','./icon-192.png','./icon-512.png'];
/* P2/SW5 fix: cache.put() keys on the full request URL including its query string, and the
   manual "Actualiser" refresh flow (refreshAppForUpdate) navigates to the main page with a
   fresh ?lp_force_reload=<timestamp> each time - so every manual refresh added a distinct,
   never-evicted entry for what is semantically the same ~1.7MB page, unbounded over the life
   of one version's cache (the activate handler below already bounds growth ACROSS versions,
   by deleting old CACHE_NAMEs entirely, but not WITHIN one). trimCache() bounds it going
   forward: cache.keys() returns entries in insertion order, so evicting the oldest beyond a
   cap is a correct, dependency-free LRU-by-age without needing a separate timestamp index. */
const MAX_CACHE_ENTRIES = 40;
async function trimCache(cache) {
  const keys = await cache.keys();
  const excess = keys.length - MAX_CACHE_ENTRIES;
  if (excess > 0) await Promise.all(keys.slice(0, excess).map(k => cache.delete(k)));
}
self.addEventListener('install', event => { event.waitUntil((async()=>{ const cache=await caches.open(CACHE_NAME); await cache.addAll(ASSETS); await self.skipWaiting(); })()); });
self.addEventListener('activate', event => { event.waitUntil((async()=>{ const keys=await caches.keys(); await Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX)&&k!==CACHE_NAME).map(k=>caches.delete(k))); await self.clients.claim(); })()); });
self.addEventListener('fetch', event => { if(event.request.method!=='GET') return; if(event.request.url.includes('version.json')) return; event.respondWith((async()=>{ const cache=await caches.open(CACHE_NAME); const cached=await cache.match(event.request, {ignoreSearch:true}); if(cached) return cached; try { const response=await fetch(event.request); if(response&&response.status===200&&response.type!=='opaque') { await cache.put(event.request,response.clone()); await trimCache(cache); } return response; } catch(error) { /* v101.7 SW3 fix: fall back to the manifest start_url (luisa_24_heures.html), not index.html — they are byte-identical today but this is the file the manifest actually declares. */ if(event.request.mode==='navigate') return cache.match('./luisa_24_heures.html'); throw error; } })()); });
