/* v102.0 R6 — conditional-state semantic-scaling closure successor; verified Update-v2 worker protocol preserved */
function scopeFingerprint(scope) {
  let h = 2166136261;
  const text = String(scope || '');
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const APP_VERSION = 'v102.0';
const BUILD_REVISION = 'R6';
const RELEASE_SEQUENCE = 102000006;
const RELEASE_ID = '24h-v102.0-r6-20260916-1ed6c3ab5d58';
const CANONICAL_SHELL = './luisa_24_heures.html';
const CANONICAL_SHELL_SHA256 = 'a42c1fba26770949970c341840de231f1630f0f7b4198c2f269898f4d11d2e21';
const SCOPE_FINGERPRINT = scopeFingerprint(self.registration.scope);
const CACHE_PREFIX = `luisa-24h-${SCOPE_FINGERPRINT}-`;
const CACHE_NAME = `${CACHE_PREFIX}v102-0-r6`;
const META_CACHE_NAME = `${CACHE_PREFIX}update-meta-v2`;
const LEGACY_MIGRATION_BASELINE_CACHE = `${CACHE_PREFIX}v101-153-r1`;
const META_KEY = new URL('./__lp24_update_meta_v2__', self.registration.scope).href;
const ASSETS = ['./index.html','./luisa_24_heures.html','./manifest.json','./apple-touch-icon.png','./favicon-16.png','./favicon-32.png','./favicon.ico','./icon-60.png','./icon-120.png','./icon-192.png','./icon-512.png','./icon-maskable-512.png'];
const MAX_CACHE_ENTRIES = 40;

function bytesToHex(buffer) { return Array.from(new Uint8Array(buffer)).map(b=>b.toString(16).padStart(2,'0')).join(''); }
async function sha256Response(response) { return bytesToHex(await crypto.subtle.digest('SHA-256', await response.arrayBuffer())); }
async function trimCache(cache) {
  const keys = await cache.keys();
  const excess = keys.length - MAX_CACHE_ENTRIES;
  if (excess > 0) await Promise.all(keys.slice(0, excess).map(k => cache.delete(k)));
}
async function readUpdateMeta() {
  try {
    const cache=await caches.open(META_CACHE_NAME);
    const response=await cache.match(META_KEY);
    return response ? await response.json() : null;
  } catch(_e) { return null; }
}
async function writeUpdateMeta(meta) {
  const cache=await caches.open(META_CACHE_NAME);
  await cache.put(META_KEY,new Response(JSON.stringify(meta),{headers:{'Content-Type':'application/json','Cache-Control':'no-store'}}));
}
async function verifiedInstall() {
  const cache=await caches.open(CACHE_NAME);
  const shellUrl=new URL(CANONICAL_SHELL,self.registration.scope).href;
  const shellResponse=await fetch(new Request(shellUrl,{cache:'reload'}));
  if (!shellResponse || !shellResponse.ok) throw new Error('canonical_shell_fetch_failed');
  const shellHash=await sha256Response(shellResponse.clone());
  if (shellHash!==CANONICAL_SHELL_SHA256) throw new Error('canonical_shell_hash_mismatch');
  await cache.put(shellUrl,shellResponse.clone());
  for (const asset of ASSETS) {
    const url=new URL(asset,self.registration.scope).href;
    if (url===shellUrl) continue;
    const response=await fetch(new Request(url,{cache:'reload'}));
    if (!response || !response.ok) throw new Error('asset_fetch_failed:'+asset);
    if (asset==='./index.html' && (await sha256Response(response.clone()))!==CANONICAL_SHELL_SHA256) throw new Error('index_shell_hash_mismatch');
    if (asset==='./manifest.json') {
      const manifest=await response.clone().json();
      if (!manifest || manifest.version!==APP_VERSION || manifest.build_revision!==BUILD_REVISION || Number(manifest.release_sequence)!==RELEASE_SEQUENCE || manifest.release_id!==RELEASE_ID || manifest.start_url!==CANONICAL_SHELL) throw new Error('manifest_release_identity_mismatch');
    }
    await cache.put(url,response);
  }
  await trimCache(cache);
}
async function pruneOwnedCachesAfterBootOk() {
  const prior=await readUpdateMeta();
  let predecessor = prior && prior.known_good_cache && prior.known_good_cache!==CACHE_NAME ? prior.known_good_cache : null;
  if (!predecessor) {
    const keys=await caches.keys();
    if (keys.includes(LEGACY_MIGRATION_BASELINE_CACHE)) predecessor=LEGACY_MIGRATION_BASELINE_CACHE;
  }
  const keep=new Set([CACHE_NAME,META_CACHE_NAME]);
  if (predecessor) keep.add(predecessor);
  const keys=await caches.keys();
  await Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX) && !keep.has(k)).map(k=>caches.delete(k)));
  await writeUpdateMeta({
    protocol:2,
    known_good_cache:CACHE_NAME,
    predecessor_cache:predecessor || null,
    release_id:RELEASE_ID,
    release_sequence:RELEASE_SEQUENCE,
    app_version:APP_VERSION,
    boot_ok_at:Date.now()
  });
}
function releaseInfoPayload() {
  return {
    type:'RELEASE_INFO_V2',
    app_version:APP_VERSION,
    build_revision:BUILD_REVISION,
    release_sequence:RELEASE_SEQUENCE,
    release_id:RELEASE_ID,
    canonical_shell:CANONICAL_SHELL,
    canonical_shell_sha256:CANONICAL_SHELL_SHA256,
    worker_state:self.serviceWorker ? self.serviceWorker.state : ''
  };
}
function reply(event,payload) {
  try { if (event.ports && event.ports[0]) event.ports[0].postMessage(payload); else if (event.source && event.source.postMessage) event.source.postMessage(payload); } catch(_e) {}
}

self.addEventListener('install', event => {
  // Intentionally no skipWaiting(): legacy v101.153 must be escaped through a controlled close/reopen boundary.
  event.waitUntil(verifiedInstall());
});
self.addEventListener('activate', event => {
  // Intentionally no clients.claim() and no cache deletion. Existing clients are not force-reloaded.
  event.waitUntil(Promise.resolve());
});
self.addEventListener('message', event => {
  const data=event.data || {};
  if (data.type==='GET_RELEASE_INFO_V2') { reply(event,releaseInfoPayload()); return; }
  if (data.type==='SKIP_WAITING') {
    // Legacy v153/v154 pages send this automatically. It is deliberately ignored because it is not provenance-safe manual consent.
    return;
  }
  if (data.type==='ACTIVATE_UPDATE_V2') {
    const ok=String(data.expected_release_id||'')===RELEASE_ID && Number(data.expected_release_sequence)===RELEASE_SEQUENCE && !!data.request_id;
    if (!ok) { reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id||null,release_id:RELEASE_ID}); return; }
    reply(event,{type:'ACTIVATE_UPDATE_ACCEPTED_V2',request_id:data.request_id,release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE});
    event.waitUntil(self.skipWaiting());
    return;
  }
  if (data.type==='BOOT_OK_V2') {
    const ok=String(data.release_id||'')===RELEASE_ID && Number(data.release_sequence)===RELEASE_SEQUENCE && String(data.app_version||'')===APP_VERSION;
    if (!ok) { reply(event,{type:'BOOT_OK_REJECTED_V2',release_id:RELEASE_ID}); return; }
    event.waitUntil((async()=>{
      await pruneOwnedCachesAfterBootOk();
      reply(event,{type:'BOOT_OK_ACCEPTED_V2',release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE});
    })());
  }
});
self.addEventListener('fetch', event => {
  if (event.request.method!=='GET') return;
  const requestUrl=new URL(event.request.url);
  if (requestUrl.origin===self.location.origin && requestUrl.pathname.endsWith('/version.json')) return;
  if (event.request.mode==='navigate') {
    event.respondWith((async()=>{
      const cache=await caches.open(CACHE_NAME);
      const cached=await cache.match(new URL(CANONICAL_SHELL,self.registration.scope).href);
      if (cached) return cached;
      try {
        const response=await fetch(new Request(new URL(CANONICAL_SHELL,self.registration.scope).href,{cache:'reload'}));
        if (response && response.ok && (await sha256Response(response.clone()))===CANONICAL_SHELL_SHA256) { await cache.put(new URL(CANONICAL_SHELL,self.registration.scope).href,response.clone()); return response; }
      } catch(_e) {}
      return new Response('Application indisponible hors ligne.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
    })());
    return;
  }
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE_NAME);
    const cached=await cache.match(event.request,{ignoreSearch:true});
    if (cached) return cached;
    try {
      const response=await fetch(event.request);
      if (response && response.status===200 && response.type!=='opaque') { await cache.put(event.request,response.clone()); await trimCache(cache); }
      return response;
    } catch(error) { throw error; }
  })());
});
