/* v114 B1 — Wave-0 data-integrity successor from exact v111.0/R36; backup classification only; corpus and personal-state architecture retained */
function scopeFingerprint(scope) {
  let h = 2166136261;
  const text = String(scope || '');
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const APP_VERSION = 'v114';
const BUILD_REVISION = 'B1';
const RELEASE_SEQUENCE = 114000001;
const RELEASE_ID = '24h-v114-b1-20260929-wave0-data-integrity';
const CANONICAL_SHELL = './luisa_24_heures.html';
const CANONICAL_SHELL_SHA256 = '8835471358271a4bd9ada059e53842220d732487cb867a749797f6f99a4b757a';
const SCOPE_FINGERPRINT = scopeFingerprint(self.registration.scope);
const CACHE_PREFIX = `luisa-24h-${SCOPE_FINGERPRINT}-`;
const CACHE_NAME = `${CACHE_PREFIX}v114-b1`;
const META_CACHE_NAME = `${CACHE_PREFIX}update-meta-v2`;
const LEGACY_MIGRATION_BASELINE_CACHE = `${CACHE_PREFIX}v101-153-r1`;
const META_KEY = new URL('./__lp24_update_meta_v2__', self.registration.scope).href;
const EXPLICIT_CLAIM_KEY = new URL('./__lp24_explicit_commit_claim_v2__', self.registration.scope).href;
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
async function armExplicitCommitClaim(requestId) {
  const cache=await caches.open(META_CACHE_NAME);
  const payload={protocol:2,release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE,request_id:String(requestId||''),armed_at:Date.now()};
  await cache.put(EXPLICIT_CLAIM_KEY,new Response(JSON.stringify(payload),{headers:{'Content-Type':'application/json','Cache-Control':'no-store'}}));
}
async function readExplicitCommitClaim() {
  const cache=await caches.open(META_CACHE_NAME);
  const response=await cache.match(EXPLICIT_CLAIM_KEY);
  return response ? await response.json() : null;
}
async function clearExplicitCommitClaim() {
  try { const cache=await caches.open(META_CACHE_NAME); await cache.delete(EXPLICIT_CLAIM_KEY); } catch(_e) {}
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
async function sameScopeWindowClients() {
  const scope=String(self.registration.scope||'');
  const list=await self.clients.matchAll({type:'window',includeUncontrolled:true});
  return list.filter(client=>{
    try { return String(client.url||'').startsWith(scope); } catch(_e) { return false; }
  });
}
async function explicitUpdateHasNoOtherLiveScopeClient(event) {
  const requesterId=event && event.source && event.source.id ? String(event.source.id) : '';
  if (!requesterId) return {ok:false,reason:'requester_client_identity_missing',clients:[]};
  const clients=await sameScopeWindowClients();
  const others=clients.filter(client=>String(client.id||'')!==requesterId);
  return {ok:others.length===0,reason:others.length?'other_scope_clients_open':null,clients,requesterId,otherCount:others.length};
}

self.addEventListener('install', event => {
  // Intentionally no skipWaiting(): legacy v101.153 must be escaped through a controlled close/reopen boundary.
  event.waitUntil(verifiedInstall());
});
self.addEventListener('activate', event => {
  // Automatic/first activation still does not seize existing clients. After a verified explicit
  // ACTIVATE_UPDATE_V2 request, claim same-scope clients so the requesting installed PWA can load
  // the successor shell instead of being served the predecessor cache again on Apple platforms.
  event.waitUntil((async()=>{
    const armed=await readExplicitCommitClaim();
    if (!armed) return;
    const ok=String(armed.release_id||'')===RELEASE_ID && Number(armed.release_sequence)===RELEASE_SEQUENCE && !!armed.request_id;
    if (!ok) { await clearExplicitCommitClaim(); throw new Error('explicit_commit_claim_identity_mismatch'); }
    await self.clients.claim();
    await clearExplicitCommitClaim();
  })());
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
    if (!ok) { reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id||null,release_id:RELEASE_ID,reason:'release_identity_mismatch'}); return; }
    event.waitUntil((async()=>{
      // R33 changes the canonical personal-state authority from localStorage to IndexedDB.
      // Never cross that migration boundary while another predecessor window is live:
      // R32 cannot participate in the new canonical store and a mixed R32/R33 writer set
      // could otherwise acknowledge changes into different authorities. Fail closed and
      // leave every current page untouched; the user can close the other window and retry.
      const isolation=await explicitUpdateHasNoOtherLiveScopeClient(event);
      if (!isolation.ok) {
        reply(event,{type:'ACTIVATE_UPDATE_REJECTED_V2',request_id:data.request_id,release_id:RELEASE_ID,reason:isolation.reason,other_scope_clients:isolation.otherCount||0});
        return;
      }
      await armExplicitCommitClaim(data.request_id);
      reply(event,{type:'ACTIVATE_UPDATE_ACCEPTED_V2',request_id:data.request_id,release_id:RELEASE_ID,release_sequence:RELEASE_SEQUENCE});
      await self.skipWaiting();
    })());
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
