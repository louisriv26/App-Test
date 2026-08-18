/* v101.85 */
const CACHE_NAME = 'luisa-24h-v101-85';
const CACHE_PREFIX = 'luisa-24h-';
const ASSETS = ['./','./index.html','./luisa_24_heures.html','./manifest.json','./apple-touch-icon.png','./favicon-16.png','./favicon-32.png','./favicon.ico','./icon-60.png','./icon-120.png','./icon-192.png','./icon-512.png','./icon-maskable-512.png'];
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
/* v101.53 FINDING-01 fix: cache.addAll() fetches with the DEFAULT cache mode, which consults the
   browser HTTP cache. A newly installing worker could therefore pull the PREVIOUS version's files
   out of the HTTP cache and store them into its OWN, new CACHE_NAME - so the cache name flipped to
   the new version while its contents were still the old build. Because the fetch handler below is
   cache-first with {ignoreSearch:true}, the ?lp_force_reload= parameter that refreshAppForUpdate()
   appends could not escape it, and the client stayed pinned to the old version indefinitely - not
   for one reload, but permanently, until storage was cleared. Reproduced end-to-end on a real
   origin: after Actualiser AND a second reload the client still ran the old build while holding the
   new cache name, and a direct Cache Storage read proved the new cache held the old HTML.
   {cache:'reload'} forces each asset to the network and refreshes the HTTP cache entry, so a new
   cache generation can never be seeded from a stale one.
   Trade-off accepted: addAll() is all-or-nothing, so an update now requires real network at install
   time. If it fails the old worker simply keeps serving - the app stays usable, the update just
   waits. That is the correct failure direction. */
self.addEventListener('install', event => { event.waitUntil((async()=>{ const cache=await caches.open(CACHE_NAME); await cache.addAll(ASSETS.map(u => new Request(u, { cache: 'reload' }))); await self.skipWaiting(); })()); });
self.addEventListener('activate', event => { event.waitUntil((async()=>{ const keys=await caches.keys(); await Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX)&&k!==CACHE_NAME).map(k=>caches.delete(k))); await self.clients.claim(); })()); });
self.addEventListener('fetch', event => { if(event.request.method!=='GET') return; if(event.request.url.includes('version.json')) return; event.respondWith((async()=>{ const cache=await caches.open(CACHE_NAME); const cached=await cache.match(event.request, {ignoreSearch:true}); if(cached) return cached; try { const response=await fetch(event.request); if(response&&response.status===200&&response.type!=='opaque') { await cache.put(event.request,response.clone()); await trimCache(cache); } return response; } catch(error) { /* v101.7 SW3 fix: fall back to the manifest start_url (luisa_24_heures.html), not index.html — they are byte-identical today but this is the file the manifest actually declares. */ if(event.request.mode==='navigate') return cache.match('./luisa_24_heures.html'); throw error; } })()); });
