<<<<<<< HEAD
const VERSION = 'ldc-v2.19.142.2-R1B-pls-owner-prototype';
const CACHE_PREFIX = 'ldc-le-livre-du-ciel-';
const OFFLINE_STORAGE_SCHEMA = 'ldc-offline-storage-v3';
const OFFLINE_CONTENT_BINDING_SCHEMA = 'ldc-offline-content-binding-v2';
const LEGACY_OFFLINE_CACHE_PREFIX = `${CACHE_PREFIX}offline-v`;
function scopeFingerprint(scope) {
  let h=2166136261;
  for(let i=0;i<scope.length;i++){h^=scope.charCodeAt(i);h=Math.imul(h,16777619);}
  return (h>>>0).toString(16).padStart(8,'0');
}
const OFFLINE_SCOPE_FINGERPRINT = scopeFingerprint(self.registration.scope);
const SCOPE_CACHE_PREFIX = `${CACHE_PREFIX}${OFFLINE_SCOPE_FINGERPRINT}-`;
const SHELL_CACHE = `${SCOPE_CACHE_PREFIX}shell-v2.19.142.1-R1B-pls-owner-prototype`;
const RUNTIME_CACHE = `${SCOPE_CACHE_PREFIX}runtime-v2.19.142.1-R1B-pls-owner-prototype`;
const LEGACY_V76_WORKER_VERSION = 'ldc-v2.19.76-R1B-report-r2';
const UPDATE_COMPAT_META_PATH = '__ldc_update_compat__.json';
const INSTALL_FETCH_NONCE = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
const OFFLINE_CACHE = `${CACHE_PREFIX}offline-persistent-v3-${OFFLINE_SCOPE_FINGERPRINT}`;
const OFFLINE_MANIFEST_URL = './offline_manifest.json';
const OFFLINE_MANIFEST_SCHEMA = 'ldc-offline-manifest-v3';
const OFFLINE_CONTENT_BINDING = '1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384';
const OFFLINE_CORPUS_MANIFEST_SHA256 = '92426c8aaac6fc7c6b8a02b0a7e00cd5870e80b805b411ae64c55e59bec1ad8b';
const OFFLINE_META_PATH = '__ldc_offline_meta__.json';
const RUNTIME_META_PATH = '__ldc_runtime_meta__.json';
const RUNTIME_MAX_ENTRIES = 48;
const RUNTIME_MAX_BYTES = 50331648;
let runtimeMutationQueue = Promise.resolve();

// Keep install small and atomic. If any shell/index resource cannot be cached, the
// installation fails and the previous active worker remains in control.
const SHELL = [
  './', './index.html', './manifest.json', './offline_manifest.json', './sw.js', './speech_model.js', './display_map.js', './interaction_anchor.js', './search_normalizer.js', './search_engine_v2.js', './search_exact_v21.js', './search_foundation_v21b.js', './search_near_v22.js', './search_worker_v2.js', './interim_user_state_migration.js', './search_semantic_pack_guard_r3.js', './search_semantic_v3_core_r4.js', './search_semantic_pack_registry_r5.js', './search_semantic_pack_lifecycle_r5.js', './pls_v15/hybrid_core_v1_5.js', './pls_v15/owner_runtime_v1_5.mjs', './icons/favicon-16.png', './icons/favicon-32.png', './icons/favicon.ico', './icons/icon-60.png', './icons/icon-120.png', './icons/apple-touch-icon.png', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png', './assets/fonts/fonts.css', './assets/fonts/im-fell-english-latin-400-normal.woff2', './assets/fonts/im-fell-english-latin-400-italic.woff2', './assets/fonts/crimson-text-latin-400-normal.woff2', './assets/fonts/crimson-text-latin-400-italic.woff2', './assets/fonts/crimson-text-latin-600-normal.woff2', './assets/icons/tabler-icons.min.css', './assets/icons/tabler-icons.woff2', './assets/js/sortable.min.js'
=======
// ── Version — must match APP_VERSION in index.html ───────────────────
const VERSION = '51.1';

// Stage 8 CACHE-SCOPE-COLL-01: Cache Storage ownership is deployment-scope
// specific. This prevents a sibling deployment on the same origin from deleting
// this installation's shell/content caches. Legacy unscoped mjv-* caches are
// intentionally left untouched during the first transition.
function scopeFingerprint(scope) {
  let h = 2166136261;
  const text = String(scope || '');
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
const SCOPE_FINGERPRINT = scopeFingerprint(self.registration.scope);
const CACHE_PREFIX = `mjv-${SCOPE_FINGERPRINT}-`;

// H5 uses two deployment-scoped buckets. Local OFL fonts ship with the release shell.
//   SHELL   — bumped per app version (index.html, manifest, icons, local fonts)
//   CONTENT — bumped when governed corpus or migration assets change
const SHELL_CACHE   = CACHE_PREFIX + 'shell-v' + VERSION;
const CONTENT_CACHE = CACHE_PREFIX + 'content-v3';   // corpus 1.0.1 + hardened migration generation
const ALL_CACHES = [SHELL_CACHE, CONTENT_CACHE];

// Icons are precached too: without them a first-run-offline install showed
// broken icons until one online visit populated the cache opportunistically.
const REQUIRED_SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './fonts/crimson-text-400.woff2',
  './fonts/crimson-text-600.woff2',
  './fonts/crimson-text-400-italic.woff2',
  './fonts/im-fell-english-400.woff2',
  './fonts/im-fell-english-400-italic.woff2',
  './fonts/OFL-Crimson-Text.txt',
  './fonts/OFL-IM-Fell-English.txt',
>>>>>>> c4ee5347db1f8e7892eafb72b74f62a3f7f85d05
];

const OPTIONAL_SHELL_ASSETS = [
  './icons/favicon-16.png',
  './icons/favicon-32.png',
  './icons/favicon.ico',
  './icons/icon-60.png',
  './icons/icon-120.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
];

<<<<<<< HEAD
function isCurrentScopeShellRuntimeCacheName(name) {
  return name.startsWith(SCOPE_CACHE_PREFIX);
}
function isOfflineFamilyCacheName(name) { return name.startsWith(`${CACHE_PREFIX}offline-`); }
function isLegacyOfflineCacheName(name) { return name.startsWith(LEGACY_OFFLINE_CACHE_PREFIX); }
function requestBelongsToCurrentScope(input) {
  const u=new URL(typeof input==='string'?input:input.url), scope=new URL(self.registration.scope);
  return u.origin===scope.origin && u.pathname.startsWith(scope.pathname);
}
function hex(buf) { return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join(''); }
async function sha256Bytes(bytes) { return hex(await crypto.subtle.digest('SHA-256', bytes)); }
async function sha256Text(text) { return sha256Bytes(new TextEncoder().encode(text)); }
function bindingCanonicalString(m) {
  const obj={
    assets:(m.assets||[]).map(a=>({bytes:Number(a.bytes),path:String(a.path),sha256:String(a.sha256)})),
    corpus_generation:m.corpus_generation,
    corpus_manifest_sha256:m.corpus_manifest_sha256,
    schema:OFFLINE_CONTENT_BINDING_SCHEMA
  };
  // Build tooling uses the same lexical key order. The digest binds content identity,
  // not app version or physical cache name.
  return JSON.stringify(obj);
}
function statusBase(m) { return {storage_schema:m&&m.storage_schema||OFFLINE_STORAGE_SCHEMA,content_binding_schema:m&&m.content_binding_schema||OFFLINE_CONTENT_BINDING_SCHEMA,content_binding_sha256:m&&m.content_binding_sha256||OFFLINE_CONTENT_BINDING,corpus_manifest_sha256:m&&m.corpus_manifest_sha256||OFFLINE_CORPUS_MANIFEST_SHA256,scope_fingerprint:OFFLINE_SCOPE_FINGERPRINT}; }
function terminalPayload(job,state,message,extra={}) {
  return {type:'LDC_OFFLINE_STATUS',state,job_id:job&&job.job_id||null,completed:job&&job.completed||0,total:job&&job.total||0,failed:job&&job.failed||[],total_bytes:job&&job.total_bytes||0,...statusBase(job&&job.manifest),message:message||'',...extra};
}
async function broadcast(payload, extraClientId) {
  const clients = await self.clients.matchAll({type:'window',includeUncontrolled:true});
  const seen=new Set();
  for(const c of clients){seen.add(c.id);c.postMessage(payload);}
  if(extraClientId&&!seen.has(extraClientId)){const c=await self.clients.get(extraClientId);if(c)c.postMessage(payload);}
}
async function loadOfflineManifest() {
  const shell=await caches.open(SHELL_CACHE);
  let r=await shell.match(OFFLINE_MANIFEST_URL,{ignoreSearch:true});
  if(!r){r=await fetch(OFFLINE_MANIFEST_URL,{cache:'reload'});if(r&&r.ok)await shell.put(OFFLINE_MANIFEST_URL,r.clone());}
  if(!r||!r.ok)throw new Error('offline manifest indisponible');
  const m=await r.json();
  if(m.schema!==OFFLINE_MANIFEST_SCHEMA||m.app_version!=='v2.19.142.2-R1B-PLS-OWNER-PROTOTYPE'||m.storage_schema!==OFFLINE_STORAGE_SCHEMA)throw new Error('offline manifest incompatible');
  if(m.content_binding_schema!==OFFLINE_CONTENT_BINDING_SCHEMA||m.content_binding_sha256!==OFFLINE_CONTENT_BINDING)throw new Error('offline manifest binding incompatible');
  if(m.corpus_manifest_sha256!==OFFLINE_CORPUS_MANIFEST_SHA256)throw new Error('offline corpus manifest binding incompatible');
  const unique=[...new Set((m.assets||[]).map(a=>a.path))];
  if(unique.length!==m.asset_count||unique.length!==(m.assets||[]).length)throw new Error('offline manifest dupliqué/incomplet');
  const actualBinding=await sha256Text(bindingCanonicalString(m));
  if(actualBinding!==OFFLINE_CONTENT_BINDING)throw new Error('offline manifest content binding invalide');
  const assetMap=new Map(m.assets.map(a=>[a.path,a]));
  return {...m,paths:unique,assetMap};
}
function cacheUrl(path) { return new URL(path,self.registration.scope).href; }
async function readOfflineMeta(cache,m) {
  const r=await cache.match(cacheUrl(OFFLINE_META_PATH),{ignoreSearch:true});if(!r)return {failed:[]};
  try{
    const x=await r.json();
    if(x.schema!=='ldc-offline-meta-v2'||x.storage_schema!==OFFLINE_STORAGE_SCHEMA||x.scope_fingerprint!==OFFLINE_SCOPE_FINGERPRINT||x.content_binding_schema!==OFFLINE_CONTENT_BINDING_SCHEMA||x.content_binding_sha256!==m.content_binding_sha256)return {failed:[]};
    return x;
  }catch(e){return {failed:[]};}
}
async function writeOfflineMeta(cache,m,failed=[]) {
  const body=JSON.stringify({schema:'ldc-offline-meta-v2',storage_schema:OFFLINE_STORAGE_SCHEMA,scope_fingerprint:OFFLINE_SCOPE_FINGERPRINT,content_binding_schema:OFFLINE_CONTENT_BINDING_SCHEMA,content_binding_sha256:m.content_binding_sha256,corpus_manifest_sha256:m.corpus_manifest_sha256,failed:Array.isArray(failed)?failed:[],updated_at:new Date().toISOString()});
  await cache.put(cacheUrl(OFFLINE_META_PATH),new Response(body,{status:200,headers:{'content-type':'application/json','x-ldc-content-binding':m.content_binding_sha256,'x-ldc-offline-storage-schema':OFFLINE_STORAGE_SCHEMA}}));
}
async function offlineCacheSources() {
  const keys=await caches.keys(), names=[OFFLINE_CACHE];
  for(const name of keys.filter(isLegacyOfflineCacheName).sort().reverse())if(!names.includes(name))names.push(name);
  const out=[];
  for(const name of names)out.push({name,cache:await caches.open(name),stable:name===OFFLINE_CACHE});
  return out;
}
async function offlineCacheEntryVerified(cache,asset,deleteInvalid=true) {
  const url=cacheUrl(asset.path);
  if(!requestBelongsToCurrentScope(url))return {ok:false,reason:'wrong scope'};
  const r=await cache.match(url,{ignoreSearch:true});if(!r)return {ok:false,reason:'missing'};
  const h=r.headers;
  const ok=h.get('x-ldc-verified-sha256')===asset.sha256 && h.get('x-ldc-verified-bytes')===String(asset.bytes);
  if(!ok&&deleteInvalid)await cache.delete(url,{ignoreSearch:true});
  return ok?{ok:true,response:r}:{ok:false,reason:'cache integrity marker mismatch'};
}
async function findVerifiedOfflineAsset(asset,sources,deleteInvalid=true) {
  let invalid=false;
  for(const source of sources){
    const v=await offlineCacheEntryVerified(source.cache,asset,deleteInvalid);
    if(v.ok)return {ok:true,response:v.response,cache_name:source.name,stable:source.stable};
    if(v.reason!=='missing')invalid=true;
  }
  return {ok:false,reason:invalid?'cache integrity marker mismatch':'missing'};
}
async function runtimeCacheEntryVerified(cache,asset,m,deleteInvalid=true) {
  const url=cacheUrl(asset.path),r=await cache.match(url,{ignoreSearch:true});if(!r)return {ok:false,reason:'missing'};
  const h=r.headers;
  const ok=h.get('x-ldc-verified-sha256')===asset.sha256 && h.get('x-ldc-verified-bytes')===String(asset.bytes) && h.get('x-ldc-content-binding')===m.content_binding_sha256;
  if(!ok&&deleteInvalid)await cache.delete(url,{ignoreSearch:true});
  return ok?{ok:true,response:r}:{ok:false,reason:'runtime cache integrity marker mismatch'};
}
function emptyRuntimeStats() { return {entries:0,bytes:0,max_entries:RUNTIME_MAX_ENTRIES,max_bytes:RUNTIME_MAX_BYTES}; }
function queueRuntimeMutation(task) {
  const next=runtimeMutationQueue.catch(()=>{}).then(task);
  runtimeMutationQueue=next.catch(()=>{});
  return next;
}
async function readRuntimeMeta(cache,m) {
  const r=await cache.match(cacheUrl(RUNTIME_META_PATH),{ignoreSearch:true});
  if(!r)return {schema:'ldc-runtime-meta-v1',cache_version:RUNTIME_CACHE,content_binding_sha256:m.content_binding_sha256,entries:[]};
  try{
    const x=await r.json();
    if(x.schema!=='ldc-runtime-meta-v1'||x.cache_version!==RUNTIME_CACHE||x.content_binding_sha256!==m.content_binding_sha256||!Array.isArray(x.entries))throw new Error('runtime meta incompatible');
    const seen=new Set(), entries=[];
    for(const e of x.entries){
      const path=String(e&&e.path||''); const asset=m.assetMap.get(path);
      if(!asset||seen.has(path))continue; seen.add(path);entries.push({path,bytes:Number(asset.bytes)});
    }
    return {schema:'ldc-runtime-meta-v1',cache_version:RUNTIME_CACHE,content_binding_sha256:m.content_binding_sha256,entries};
  }catch(e){return {schema:'ldc-runtime-meta-v1',cache_version:RUNTIME_CACHE,content_binding_sha256:m.content_binding_sha256,entries:[]};}
}
async function writeRuntimeMeta(cache,m,entries) {
  const clean=(entries||[]).map(e=>({path:String(e.path),bytes:Number(e.bytes)}));
  const body=JSON.stringify({schema:'ldc-runtime-meta-v1',cache_version:RUNTIME_CACHE,content_binding_sha256:m.content_binding_sha256,entries:clean});
  await cache.put(cacheUrl(RUNTIME_META_PATH),new Response(body,{status:200,headers:{'content-type':'application/json','x-ldc-content-binding':m.content_binding_sha256}}));
}
async function recordRuntimeEntry(asset,m) {
  return queueRuntimeMutation(async()=>{
    const cache=await caches.open(RUNTIME_CACHE), meta=await readRuntimeMeta(cache,m);
    let entries=meta.entries.filter(e=>e.path!==asset.path); entries.push({path:asset.path,bytes:Number(asset.bytes)});
    let total=entries.reduce((a,e)=>a+Number(e.bytes||0),0);
    const pinned=new Set(BOOT_CRITICAL_CORPUS);
    while(entries.length>1&&(entries.length>RUNTIME_MAX_ENTRIES||total>RUNTIME_MAX_BYTES)){
      const victimIndex=entries.findIndex(e=>!pinned.has(e.path));
      if(victimIndex<0)break;
      const victim=entries.splice(victimIndex,1)[0]; total-=Number(victim.bytes||0); await cache.delete(cacheUrl(victim.path),{ignoreSearch:true});
    }
    await writeRuntimeMeta(cache,m,entries);
    return {entries:entries.length,bytes:total,max_entries:RUNTIME_MAX_ENTRIES,max_bytes:RUNTIME_MAX_BYTES};
  });
}
async function runtimeCacheStats(m) {
  await runtimeMutationQueue.catch(()=>{});
  const cache=await caches.open(RUNTIME_CACHE), meta=await readRuntimeMeta(cache,m), valid=[];
  for(const e of meta.entries){
    const asset=m.assetMap.get(e.path); if(!asset)continue;
    const hit=await cache.match(cacheUrl(e.path),{ignoreSearch:true}); if(!hit)continue;
    const h=hit.headers;
    if(h.get('x-ldc-verified-sha256')===asset.sha256&&h.get('x-ldc-verified-bytes')===String(asset.bytes)&&h.get('x-ldc-content-binding')===m.content_binding_sha256)valid.push({path:e.path,bytes:Number(asset.bytes)});
    else await cache.delete(cacheUrl(e.path),{ignoreSearch:true});
  }
  if(valid.length!==meta.entries.length)await writeRuntimeMeta(cache,m,valid);
  return {entries:valid.length,bytes:valid.reduce((a,e)=>a+e.bytes,0),max_entries:RUNTIME_MAX_ENTRIES,max_bytes:RUNTIME_MAX_BYTES};
}
async function clearRuntimeCache() {
  return queueRuntimeMutation(async()=>{
    const m=await loadOfflineManifest(),cache=await caches.open(RUNTIME_CACHE),kept=[];
    const requests=await cache.keys();
    for(const request of requests){
      const path=corpusAssetPath(request);
      if(BOOT_CRITICAL_CORPUS.includes(path))continue;
      if(path===RUNTIME_META_PATH)continue;
      await cache.delete(request,{ignoreSearch:true});
    }
    for(const path of BOOT_CRITICAL_CORPUS){
      const asset=m.assetMap.get(path);if(!asset)continue;
      const hit=await verifiedRuntimeCachedCorpusHit(cache,new Request(cacheUrl(path)),asset,m);
      if(hit)kept.push({path,bytes:Number(asset.bytes)});
    }
    await writeRuntimeMeta(cache,m,kept);
    return {entries:kept.length,bytes:kept.reduce((a,e)=>a+e.bytes,0),max_entries:RUNTIME_MAX_ENTRIES,max_bytes:RUNTIME_MAX_BYTES};
  });
}
async function pruneObsoleteStableOfflineEntries(cache,m) {
  const requests=await cache.keys();let removed=0;
  for(const request of requests){
    if(!requestBelongsToCurrentScope(request))continue;
    const path=corpusAssetPath(request);
    if(!path.startsWith('corpus/'))continue;
    if(m.assetMap.has(path))continue;
    if(await cache.delete(request,{ignoreSearch:true}))removed++;
  }
  return removed;
}
async function scanOfflineCache() {
  const m=await loadOfflineManifest(), sources=await offlineCacheSources(), stable=sources[0].cache;
  await pruneObsoleteStableOfflineEntries(stable,m);
  let completed=0,cached_bytes=0;const invalid=[];const missing=[];
  for(const asset of m.assets){
    const v=await findVerifiedOfflineAsset(asset,sources,true);
    if(v.ok){completed++;cached_bytes+=Number(asset.bytes||0);}else if(v.reason==='missing')missing.push(asset.path);else invalid.push({path:asset.path,error:v.reason});
  }
  const meta=await readOfflineMeta(stable,m),unresolved=new Map();
  for(const f of (meta.failed||[])){if(f&&f.path&&!unresolved.has(f.path))unresolved.set(f.path,f);}
  for(const f of invalid){if(f&&f.path)unresolved.set(f.path,f);}
  const missingSet=new Set(missing),failed=[...unresolved.values()].filter(f=>missingSet.has(f.path)||invalid.some(x=>x.path===f.path));
  const state=completed===m.assets.length?'READY':(completed?'PARTIAL':'NOT_PREPARED');
  if(state==='READY'&&failed.length)failed.length=0;
  await writeOfflineMeta(stable,m,failed);
  const runtime=await runtimeCacheStats(m);
  return {state,completed,total:m.assets.length,failed,total_bytes:m.total_bytes||0,cached_bytes,job_id:null,...statusBase(m),runtime,message:state==='READY'?'Préparation complète.':''};
}
async function verifiedNetworkResponse(res,asset,m) {
  if(!res||!res.ok)throw new Error(`HTTP ${res&&res.status}`);
  const bytes=await res.arrayBuffer();
  if(bytes.byteLength!==Number(asset.bytes))throw new Error(`integrity size mismatch: attendu ${asset.bytes}, reçu ${bytes.byteLength}`);
  const digest=await sha256Bytes(bytes);
  if(digest!==asset.sha256)throw new Error(`integrity sha256 mismatch: attendu ${asset.sha256}, reçu ${digest}`);
  const headers=new Headers(res.headers);headers.set('x-ldc-verified-sha256',asset.sha256);headers.set('x-ldc-verified-bytes',String(asset.bytes));headers.set('x-ldc-content-binding',m.content_binding_sha256);
  return new Response(bytes,{status:res.status,statusText:res.statusText,headers});
}
async function fetchIntoOfflineCache(cache,asset,job) {
  const url=cacheUrl(asset.path),ctl=new AbortController();job.controllers.add(ctl);
  const timer=setTimeout(()=>ctl.abort('timeout'),FILE_TIMEOUT_MS);
  try{
    const res=await fetch(url,{cache:'reload',signal:ctl.signal});
    const verified=await verifiedNetworkResponse(res,asset,job.manifest);
    await cache.put(url,verified);return true;
  }finally{clearTimeout(timer);job.controllers.delete(ctl);}
}
async function runOfflineJob(job,requestClientId) {
  try{
    job.state='CHECKING';await broadcast(terminalPayload(job,'CHECKING','Analyse des fichiers déjà présents…'),requestClientId);
    const m=await loadOfflineManifest();job.manifest=m;job.total=m.assets.length;job.total_bytes=m.total_bytes||0;
    const sources=await offlineCacheSources(),stable=sources[0].cache,missing=[];job.completed=0;job.failed=[];
    await pruneObsoleteStableOfflineEntries(stable,m);
    for(const asset of m.assets){if(job.cancelled)break;const v=await findVerifiedOfflineAsset(asset,sources,true);if(v.ok)job.completed++;else missing.push(asset);}
    if(job.cancelled){job.state='CANCELLED';await writeOfflineMeta(stable,m,job.failed);await broadcast(terminalPayload(job,'CANCELLED','Préparation annulée; les fichiers déjà vérifiés sont conservés.'),requestClientId);return;}
    if(!missing.length){job.state='READY';await writeOfflineMeta(stable,m,[]);const runtime=await clearRuntimeCache();await broadcast(terminalPayload(job,'READY','Préparation complète.',{runtime}),requestClientId);return;}
    job.state='DOWNLOADING';await broadcast(terminalPayload(job,'DOWNLOADING','Téléchargement et vérification des fichiers manquants…'),requestClientId);
    let cursor=0;
    async function worker(){
      while(true){
        if(job.cancelled)return;const i=cursor++;if(i>=missing.length)return;const asset=missing[i];
        try{await fetchIntoOfflineCache(stable,asset,job);job.completed++;}
        catch(e){if(job.cancelled)return;job.failed.push({path:asset.path,error:(e&&e.name==='AbortError')?'timeout/annulation':String(e&&e.message||e)});}
        await writeOfflineMeta(stable,m,job.failed);
        await broadcast(terminalPayload(job,'DOWNLOADING',job.failed.length?'Téléchargement avec certains échecs…':'Téléchargement et vérification…'),requestClientId);
      }
    }
    await Promise.all(Array.from({length:Math.min(DOWNLOAD_CONCURRENCY,missing.length)},()=>worker()));
    if(job.cancelled){job.state='CANCELLED';await writeOfflineMeta(stable,m,job.failed);await broadcast(terminalPayload(job,'CANCELLED','Préparation annulée; les fichiers déjà vérifiés sont conservés.'),requestClientId);return;}
    if(job.failed.length){job.state=job.completed?'PARTIAL':'ERROR';await writeOfflineMeta(stable,m,job.failed);await broadcast(terminalPayload(job,job.state,'Certains fichiers n’ont pas pu être vérifiés. Utilisez Reprendre.'),requestClientId);return;}
    job.state='READY';await writeOfflineMeta(stable,m,[]);const runtime=await clearRuntimeCache();await broadcast(terminalPayload(job,'READY','Préparation complète et vérifiée.',{runtime}),requestClientId);
  }catch(e){
    job.state='ERROR';job.failed=job.failed||[];
    if(job.manifest){try{const stable=(await offlineCacheSources())[0].cache;await writeOfflineMeta(stable,job.manifest,job.failed);}catch(_){}}
    await broadcast(terminalPayload(job,'ERROR',String(e&&e.message||e)),requestClientId);
  }finally{offlineJob=null;}
}
async function clearCurrentScopeOfflineData() {
  await caches.delete(OFFLINE_CACHE);
  const keys=await caches.keys();
  for(const name of keys.filter(isLegacyOfflineCacheName)){
    const cache=await caches.open(name),requests=await cache.keys();
    for(const request of requests)if(requestBelongsToCurrentScope(request))await cache.delete(request,{ignoreSearch:true});
    if((await cache.keys()).length===0)await caches.delete(name);
  }
}
async function handleOfflineMessage(event) {
  const d=event.data||{}, clientId=event.source&&event.source.id;
  if(d.type==='OFFLINE_STATUS'){
    if(offlineJob){await broadcast(terminalPayload(offlineJob,offlineJob.state,'Préparation en cours.',{request_id:d.request_id||null}),clientId);return;}
    try{const st=await scanOfflineCache();await broadcast({type:'LDC_OFFLINE_STATUS',...st,request_id:d.request_id||null},clientId);}
    catch(e){await broadcast({type:'LDC_OFFLINE_STATUS',state:'ERROR',completed:0,total:0,failed:[],total_bytes:0,job_id:null,content_binding_sha256:OFFLINE_CONTENT_BINDING,corpus_manifest_sha256:OFFLINE_CORPUS_MANIFEST_SHA256,request_id:d.request_id||null,message:String(e&&e.message||e)},clientId);}return;
  }
  if(d.type==='OFFLINE_PREPARE'){
    if(offlineJob){await broadcast({...terminalPayload(offlineJob,offlineJob.state,'Préparation déjà en cours; cette fenêtre y est rattachée.'),attached:true},clientId);return;}
    offlineJob={job_id:d.job_id||`sw-${Date.now()}`,state:'CHECKING',completed:0,total:0,total_bytes:0,failed:[],cancelled:false,controllers:new Set(),manifest:null};
    await runOfflineJob(offlineJob,clientId);return;
  }
  if(d.type==='OFFLINE_CANCEL'){
    if(offlineJob&&(!d.job_id||d.job_id===offlineJob.job_id)){offlineJob.cancelled=true;for(const c of offlineJob.controllers)try{c.abort('cancelled')}catch(e){};await broadcast(terminalPayload(offlineJob,'CANCELLED','Annulation demandée.'),clientId);}
    else{const st=await scanOfflineCache();await broadcast({type:'LDC_OFFLINE_STATUS',...st,message:'Aucune préparation active.'},clientId);}return;
  }
  if(d.type==='OFFLINE_CLEAR'){
    if(offlineJob){await broadcast(terminalPayload(offlineJob,offlineJob.state,'Impossible d’effacer pendant un téléchargement.'),clientId);return;}
    await clearCurrentScopeOfflineData();const runtime=await clearRuntimeCache();const m=await loadOfflineManifest();await broadcast({type:'LDC_OFFLINE_STATUS',state:'NOT_PREPARED',completed:0,total:m.assets.length,failed:[],total_bytes:m.total_bytes||0,cached_bytes:0,job_id:null,...statusBase(m),runtime,message:'Données hors ligne de cette installation et cache temporaire de lecture/recherche effacés.'},clientId);return;
  }
=======
const CONTENT_ASSETS = [
  './corpus/manifest.json?cv=1.0.1',
  './corpus/days.json?cv=1.0.1',
  './corpus/migrations-v1.0.0-to-v1.0.1.json?mv=2.17.18'
];


// How long to wait for the network before falling back to a cached copy.
// Without this, a "lie-fi" connection left the app on the loading screen for
// the full request timeout even though a perfectly good cached copy existed.
const NET_TIMEOUT_MS = 3500;

// Install-time requests bypass the browser HTTP cache. This prevents a new
// service-worker version from seeding its versioned shell cache with stale
// bytes that happen to be fresh in the normal HTTP cache. Required reader
// assets are atomic: if one cannot be obtained, this worker does not activate
// and the previous working service worker remains in control.
function scopedRequest(url, cacheMode = 'reload') {
  return new Request(new URL(url, self.registration.scope).href, { cache: cacheMode });
>>>>>>> c4ee5347db1f8e7892eafb72b74f62a3f7f85d05
}

async function fetchRequired(url) {
  const req = scopedRequest(url, 'reload');
  const res = await fetch(req);
  if (!res || !res.ok) throw new Error('required precache failed: ' + req.url);
  return { req, res };
}

async function putRequired(cache, url) {
  const { req, res } = await fetchRequired(url);
  await cache.put(req, res.clone());
}

async function putOptionalReload(cache, url) {
  try {
    const { req, res } = await fetchRequired(url);
    await cache.put(req, res.clone());
  } catch (_) { /* cosmetic asset: fallback UI remains usable */ }
}

async function ensureContent(cache, url) {
  const req = scopedRequest(url, 'reload');
  if (await cache.match(req)) return;
  const res = await fetch(req);
  if (!res || !res.ok) throw new Error('required content precache failed: ' + req.url);
  await cache.put(req, res.clone());
}



self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL_CACHE);
    for (const u of REQUIRED_SHELL_ASSETS) await putRequired(shell, u);
    await Promise.all(OPTIONAL_SHELL_ASSETS.map(u => putOptionalReload(shell, u)));

    const content = await caches.open(CONTENT_CACHE);
    for (const u of CONTENT_ASSETS) await ensureContent(content, u);

    await self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    // Only touch older caches from this exact deployment scope. Ambiguous
    // legacy unscoped mjv-* caches and sibling deployment caches are preserved.
    await Promise.all(
      keys.filter(k => k.startsWith(CACHE_PREFIX) && !ALL_CACHES.includes(k))
          .map(k => caches.delete(k))
    );
    await self.clients.claim();
    const clients = await self.clients.matchAll({ type: 'window' });
    clients.forEach(c => c.postMessage({ type: 'SW_UPDATED', version: VERSION }));
  })());
});

// Serve from cache immediately, then refresh the cache in the background so the
// next launch is up to date. Used for the corpus, which is static text that
// only changes on a deliberate content release.
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  const network = fetch(request).then(res => {
    if (res && res.status === 200) cache.put(request, res.clone());
    return res;
  }).catch(() => null);
  if (cached) return cached;              // instant, no network wait
  const fresh = await network;
  if (fresh) return fresh;
  throw new Error('offline and not cached: ' + request.url);
}

// Prefer the network so a new deployment is picked up, but never let a slow
// connection block startup: whichever resolves first within the timeout wins,
// and the cached copy is the fallback.
function shellCacheKey(request) {
  // Deep links are query-string routes served by the same app shell. The
  // install cache contains only './' and './index.html'; matching the full
  // navigation URL would therefore fail offline for ?open=unit/search routes.
  // Canonicalise only shell navigations, while preserving the browser's real
  // URL so startup routing still sees window.location.search.
  const url = new URL(request.url);
  if (url.origin === self.location.origin &&
      (url.pathname.endsWith('/') || url.pathname.endsWith('/index.html'))) {
    url.search = '';
    url.hash = '';
    return new Request(url.href, { method: 'GET' });
  }
  return request;
}

async function networkFirstWithTimeout(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cacheKey = shellCacheKey(request);
  const cached = await cache.match(cacheKey);

  const network = fetch(request, { cache: 'no-store' }).then(res => {
    if (res && res.status === 200) cache.put(cacheKey, res.clone());
    return res;
  });

  if (!cached) return network;            // nothing to fall back to

  let timer;
  const timeout = new Promise(resolve => { timer = setTimeout(() => resolve(null), NET_TIMEOUT_MS); });
  try {
    const winner = await Promise.race([network.catch(() => null), timeout]);
    return winner || cached;
  } finally {
    clearTimeout(timer);
  }
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  const res = await fetch(request);
  if (res && res.status === 200 && request.method === 'GET') cache.put(request, res.clone());
  return res;
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  const url = new URL(e.request.url);
  const isCrossOrigin = url.origin !== self.location.origin;
  const isCorpus = url.pathname.includes('/corpus/');
  const isShell = url.pathname.endsWith('/') || url.pathname.endsWith('index.html');

  if (isCrossOrigin) return;

  if (isCorpus) {
    // Static book content — serve instantly from cache, refresh in background
    e.respondWith(staleWhileRevalidate(e.request, CONTENT_CACHE));
    return;
  }

  if (isShell) {
    // Fresh shell after a deploy, but bounded so lie-fi can't stall startup
    e.respondWith(networkFirstWithTimeout(e.request, SHELL_CACHE));
    return;
  }

  e.respondWith(cacheFirst(e.request, SHELL_CACHE));
});
