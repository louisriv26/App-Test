const VERSION = 'ldc-v2.19.60-R1B';
const CACHE_PREFIX = 'ldc-le-livre-du-ciel-';
const SHELL_CACHE = `${CACHE_PREFIX}shell-v2.19.60-R1B`;
const RUNTIME_CACHE = `${CACHE_PREFIX}runtime-v2.19.60-R1B`;
const OFFLINE_CACHE = 'ldc-le-livre-du-ciel-offline-v2.19.60-R1B';
const OFFLINE_MANIFEST_URL = './offline_manifest.json';
const OFFLINE_MANIFEST_SCHEMA = 'ldc-offline-manifest-v2';
const OFFLINE_CONTENT_BINDING = '704dd1aa51805c1b4bb9a569b63e7f8db44c9c3d2bb8099f1b15b2d539ee487c';
const OFFLINE_CORPUS_MANIFEST_SHA256 = '2aa33eb3e96ca719a7e4778e1505b075a3a6bd6d283b1f63c95552bead31f9c1';
const OFFLINE_META_PATH = '__ldc_offline_meta__.json';
const RUNTIME_META_PATH = '__ldc_runtime_meta__.json';
const RUNTIME_MAX_ENTRIES = 48;
const RUNTIME_MAX_BYTES = 50331648;
let runtimeMutationQueue = Promise.resolve();

// Keep install small and atomic. If any shell/index resource cannot be cached, the
// installation fails and the previous active worker remains in control.
const SHELL = [
  './', './index.html', './manifest.json', './offline_manifest.json', './sw.js', './speech_model.js', './display_map.js', './interaction_anchor.js', './search_normalizer.js', './icons/favicon-16.png', './icons/favicon-32.png', './icons/favicon.ico', './icons/icon-60.png', './icons/icon-120.png', './icons/apple-touch-icon.png', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png', './assets/fonts/fonts.css', './assets/fonts/im-fell-english-latin-400-normal.woff2', './assets/fonts/im-fell-english-latin-400-italic.woff2', './assets/fonts/crimson-text-latin-400-normal.woff2', './assets/fonts/crimson-text-latin-400-italic.woff2', './assets/fonts/crimson-text-latin-600-normal.woff2', './assets/icons/tabler-icons.min.css', './assets/icons/tabler-icons.woff2', './assets/js/sortable.min.js'
];

let offlineJob = null;
const FILE_TIMEOUT_MS = 30000;
const DOWNLOAD_CONCURRENCY = 3;

function isOwnedCacheName(name) {
  return name.startsWith(CACHE_PREFIX) || /^ldc-v\d/.test(name);
}
function hex(buf) { return [...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join(''); }
async function sha256Bytes(bytes) { return hex(await crypto.subtle.digest('SHA-256', bytes)); }
async function sha256Text(text) { return sha256Bytes(new TextEncoder().encode(text)); }
function bindingCanonicalString(m) {
  const obj={
    app_version:m.app_version,
    assets:(m.assets||[]).map(a=>({bytes:Number(a.bytes),path:String(a.path),sha256:String(a.sha256)})),
    cache_version:m.cache_version,
    corpus_generation:m.corpus_generation,
    corpus_manifest_sha256:m.corpus_manifest_sha256,
    schema:'ldc-offline-content-binding-v1'
  };
  // Python build uses sort_keys=True; construct the same lexical top-level key order and
  // each asset in bytes,path,sha256 order. JSON.stringify preserves insertion order.
  return JSON.stringify(obj);
}
function statusBase(m) { return {content_binding_sha256:m&&m.content_binding_sha256||OFFLINE_CONTENT_BINDING,corpus_manifest_sha256:m&&m.corpus_manifest_sha256||OFFLINE_CORPUS_MANIFEST_SHA256}; }
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
  if(m.schema!==OFFLINE_MANIFEST_SCHEMA||m.app_version!=='v2.19.60-R1B'||m.cache_version!==OFFLINE_CACHE)throw new Error('offline manifest incompatible');
  if(m.content_binding_schema!=='ldc-offline-content-binding-v1'||m.content_binding_sha256!==OFFLINE_CONTENT_BINDING)throw new Error('offline manifest binding incompatible');
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
  try{const x=await r.json();if(x.content_binding_sha256!==m.content_binding_sha256||x.cache_version!==m.cache_version)return {failed:[]};return x;}catch(e){return {failed:[]};}
}
async function writeOfflineMeta(cache,m,failed=[]) {
  const body=JSON.stringify({schema:'ldc-offline-meta-v1',cache_version:m.cache_version,content_binding_sha256:m.content_binding_sha256,corpus_manifest_sha256:m.corpus_manifest_sha256,failed:Array.isArray(failed)?failed:[],updated_at:new Date().toISOString()});
  await cache.put(cacheUrl(OFFLINE_META_PATH),new Response(body,{status:200,headers:{'content-type':'application/json','x-ldc-content-binding':m.content_binding_sha256}}));
}
async function cacheEntryVerified(cache,asset,m,deleteInvalid=true) {
  const url=cacheUrl(asset.path), r=await cache.match(url,{ignoreSearch:true});if(!r)return {ok:false,reason:'missing'};
  const h=r.headers;
  const ok=h.get('x-ldc-verified-sha256')===asset.sha256 && h.get('x-ldc-verified-bytes')===String(asset.bytes) && h.get('x-ldc-content-binding')===m.content_binding_sha256;
  if(!ok&&deleteInvalid)await cache.delete(url);
  return ok?{ok:true}:{ok:false,reason:'cache integrity marker mismatch'};
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
    while(entries.length>1&&(entries.length>RUNTIME_MAX_ENTRIES||total>RUNTIME_MAX_BYTES)){
      const victim=entries.shift(); total-=Number(victim.bytes||0); await cache.delete(cacheUrl(victim.path),{ignoreSearch:true});
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
  return queueRuntimeMutation(async()=>{await caches.delete(RUNTIME_CACHE);return emptyRuntimeStats();});
}
async function scanOfflineCache() {
  const m=await loadOfflineManifest(), cache=await caches.open(OFFLINE_CACHE); let completed=0,cached_bytes=0;const invalid=[];const missing=[];
  for(const asset of m.assets){const v=await cacheEntryVerified(cache,asset,m,true);if(v.ok){completed++;cached_bytes+=Number(asset.bytes||0);}else if(v.reason==='missing')missing.push(asset.path);else invalid.push({path:asset.path,error:v.reason});}
  const meta=await readOfflineMeta(cache,m);const unresolved=new Map();
  for(const f of (meta.failed||[])){if(f&&f.path&&!unresolved.has(f.path))unresolved.set(f.path,f);}
  for(const f of invalid){if(f&&f.path)unresolved.set(f.path,f);}
  const missingSet=new Set(missing);
  const failed=[...unresolved.values()].filter(f=>missingSet.has(f.path)||invalid.some(x=>x.path===f.path));
  const state=completed===m.assets.length?'READY':(completed?'PARTIAL':'NOT_PREPARED');
  if(state==='READY'&&failed.length)failed.length=0;
  await writeOfflineMeta(cache,m,failed);
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
  const url=cacheUrl(asset.path);
  const ctl=new AbortController(); job.controllers.add(ctl);
  const timer=setTimeout(()=>ctl.abort('timeout'),FILE_TIMEOUT_MS);
  try{
    const res=await fetch(url,{cache:'reload',signal:ctl.signal});
    const verified=await verifiedNetworkResponse(res,asset,job.manifest);
    await cache.put(url,verified); return true;
  }finally{clearTimeout(timer);job.controllers.delete(ctl);}
}
async function runOfflineJob(job,requestClientId) {
  try{
    job.state='CHECKING'; await broadcast(terminalPayload(job,'CHECKING','Analyse du cache existant…'),requestClientId);
    const m=await loadOfflineManifest(); job.manifest=m;job.total=m.assets.length;job.total_bytes=m.total_bytes||0;
    const cache=await caches.open(OFFLINE_CACHE), missing=[];job.completed=0;job.failed=[];
    for(const asset of m.assets){if(job.cancelled)break;const v=await cacheEntryVerified(cache,asset,m,true);if(v.ok)job.completed++;else missing.push(asset);}
    if(job.cancelled){job.state='CANCELLED';await writeOfflineMeta(cache,m,job.failed);await broadcast(terminalPayload(job,'CANCELLED','Préparation annulée.'),requestClientId);return;}
    if(!missing.length){job.state='READY';await writeOfflineMeta(cache,m,[]);const runtime=await clearRuntimeCache();await broadcast(terminalPayload(job,'READY','Préparation complète.',{runtime}),requestClientId);return;}
    job.state='DOWNLOADING';await broadcast(terminalPayload(job,'DOWNLOADING','Téléchargement et vérification des fichiers manquants…'),requestClientId);
    let cursor=0;
    async function worker(){
      while(true){
        if(job.cancelled)return; const i=cursor++; if(i>=missing.length)return; const asset=missing[i];
        try{await fetchIntoOfflineCache(cache,asset,job);job.completed++;}
        catch(e){if(job.cancelled)return;job.failed.push({path:asset.path,error:(e&&e.name==='AbortError')?'timeout/annulation':String(e&&e.message||e)});}
        await writeOfflineMeta(cache,m,job.failed);
        await broadcast(terminalPayload(job,'DOWNLOADING',job.failed.length?'Téléchargement avec certains échecs…':'Téléchargement et vérification…'),requestClientId);
      }
    }
    await Promise.all(Array.from({length:Math.min(DOWNLOAD_CONCURRENCY,missing.length)},()=>worker()));
    if(job.cancelled){job.state='CANCELLED';await writeOfflineMeta(cache,m,job.failed);await broadcast(terminalPayload(job,'CANCELLED','Préparation annulée; les fichiers déjà vérifiés sont conservés.'),requestClientId);return;}
    if(job.failed.length){job.state=job.completed?'PARTIAL':'ERROR';await writeOfflineMeta(cache,m,job.failed);await broadcast(terminalPayload(job,job.state,'Certains fichiers n’ont pas pu être vérifiés. Utilisez Reprendre.'),requestClientId);return;}
    job.state='READY';await writeOfflineMeta(cache,m,[]);const runtime=await clearRuntimeCache();await broadcast(terminalPayload(job,'READY','Préparation complète et vérifiée.',{runtime}),requestClientId);
  }catch(e){job.state='ERROR';job.failed=job.failed||[];if(job.manifest){try{const cache=await caches.open(OFFLINE_CACHE);await writeOfflineMeta(cache,job.manifest,job.failed);}catch(_){}}await broadcast(terminalPayload(job,'ERROR',String(e&&e.message||e)),requestClientId);}
  finally{offlineJob=null;}
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
    await caches.delete(OFFLINE_CACHE);const runtime=await clearRuntimeCache();const m=await loadOfflineManifest();await broadcast({type:'LDC_OFFLINE_STATUS',state:'NOT_PREPARED',completed:0,total:m.assets.length,failed:[],total_bytes:m.total_bytes||0,cached_bytes:0,job_id:null,...statusBase(m),runtime,message:'Données hors ligne et cache temporaire de lecture/recherche effacés.'},clientId);return;
  }
}

self.addEventListener('message',e=>{
  if(e.data&&e.data.type==='LDC_GET_VERSION'){const p=e.ports&&e.ports[0];if(p)p.postMessage({type:'LDC_SW_VERSION',version:VERSION});else if(e.source)e.source.postMessage({type:'LDC_SW_VERSION',version:VERSION});return;}
  if(e.data&&e.data.type==='SKIP_WAITING'){self.skipWaiting();return;}
  if(e.data&&String(e.data.type||'').startsWith('OFFLINE_'))e.waitUntil(handleOfflineMessage(e));
});

const BOOT_CRITICAL_CORPUS = ['corpus/supplements.json','corpus/supplement_manifest.json'];
async function installFreshShell() {
  await caches.delete(SHELL_CACHE);
  const c=await caches.open(SHELL_CACHE);
  const requests=SHELL.map(u=>new Request(new URL(u,self.registration.scope).href,{cache:'reload'}));
  try{await c.addAll(requests);}
  catch(e){await caches.delete(SHELL_CACHE);throw e;}
}
async function installVerifiedBootCorpus() {
  const m=await loadOfflineManifest();
  await caches.delete(RUNTIME_CACHE);
  const cache=await caches.open(RUNTIME_CACHE), entries=[];
  try{
    for(const path of BOOT_CRITICAL_CORPUS){
      const asset=m.assetMap.get(path);if(!asset)throw new Error(`boot-critical asset absent du manifeste: ${path}`);
      const raw=await fetch(cacheUrl(path),{cache:'reload'});
      const verified=await verifiedNetworkResponse(raw,asset,m);
      await cache.put(cacheUrl(path),verified.clone());entries.push({path,bytes:Number(asset.bytes)});
    }
    await writeRuntimeMeta(cache,m,entries);
  }catch(e){await caches.delete(RUNTIME_CACHE);throw e;}
}
self.addEventListener('install',e=>{e.waitUntil((async()=>{await installFreshShell();await installVerifiedBootCorpus();})());});
self.addEventListener('activate',e=>{e.waitUntil((async()=>{
  const keep=new Set([SHELL_CACHE,RUNTIME_CACHE,OFFLINE_CACHE]);
  const keys=await caches.keys();
  await Promise.all(keys.filter(k=>isOwnedCacheName(k)&&!keep.has(k)).map(k=>caches.delete(k)));
  await self.clients.claim();
})());});

function corpusAssetPath(request) {
  const u=new URL(request.url), scopePath=new URL(self.registration.scope).pathname;
  let p=u.pathname.startsWith(scopePath)?u.pathname.slice(scopePath.length):u.pathname.replace(/^\/+/, '');
  return p.replace(/^\/+/, '');
}
async function verifiedCachedCorpusHit(cache,request,asset,m) {
  const hit=await cache.match(request,{ignoreSearch:true}); if(!hit)return null;
  const h=hit.headers;
  const ok=h.get('x-ldc-verified-sha256')===asset.sha256 && h.get('x-ldc-verified-bytes')===String(asset.bytes) && h.get('x-ldc-content-binding')===m.content_binding_sha256;
  if(!ok){await cache.delete(request,{ignoreSearch:true});return null;}
  return hit;
}
async function cachedCorpusResponse(request,networkFirst=false) {
  const m=await loadOfflineManifest(), asset=m.assetMap.get(corpusAssetPath(request));
  if(!asset)return fetch(new Request(request,{cache:'reload'}));
  const offline=await caches.open(OFFLINE_CACHE), runtime=await caches.open(RUNTIME_CACHE);
  if(!networkFirst){
    const oc=await verifiedCachedCorpusHit(offline,request,asset,m); if(oc)return oc;
    const rc=await verifiedCachedCorpusHit(runtime,request,asset,m); if(rc)return rc;
  }
  try{
    const raw=await fetch(new Request(request,{cache:'reload'}));
    const verified=await verifiedNetworkResponse(raw,asset,m);
    await runtime.put(request,verified.clone()); await recordRuntimeEntry(asset,m); return verified;
  }catch(e){
    const oc=await verifiedCachedCorpusHit(offline,request,asset,m); if(oc)return oc;
    const rc=await verifiedCachedCorpusHit(runtime,request,asset,m); if(rc)return rc;
    return Response.error();
  }
}
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const url=new URL(e.request.url);if(url.origin!==self.location.origin)return;
  const path=url.pathname;
  if(path.endsWith('/version.json')){
    e.respondWith(fetch(new Request(e.request,{cache:'no-store'})));return;
  }
  if(e.request.mode==='navigate'){
    const freshNav=new Request(e.request,{cache:'reload'});
    e.respondWith(fetch(freshNav).catch(async()=>{const c=await caches.open(SHELL_CACHE);return (await c.match('./index.html'))||(await c.match('./'));}));return;
  }
  if(path.includes('/corpus/')){
    e.respondWith(cachedCorpusResponse(e.request,false));return;
  }
  e.respondWith(fetch(e.request).catch(async()=>{const c=await caches.open(SHELL_CACHE);return (await c.match(e.request,{ignoreSearch:true}))||Response.error();}));
});
