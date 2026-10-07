import http from 'node:http';import fs from 'node:fs';import {chromium} from 'playwright';
const DB='ldc_user_v1',STORE='__origin_probe',KEY='ldc_origin_probe',CACHE='ldc-origin-probe-identical-name';
const html=`<!doctype html><meta charset="utf-8"><title>origin probe</title><script>
const DB=${JSON.stringify(DB)},STORE=${JSON.stringify(STORE)},KEY=${JSON.stringify(KEY)},CACHE=${JSON.stringify(CACHE)};
function req(r){return new Promise((res,rej)=>{r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)})}
async function db(){return await new Promise((res,rej)=>{const r=indexedDB.open(DB,4);r.onupgradeneeded=()=>{const d=r.result;if(!d.objectStoreNames.contains(STORE))d.createObjectStore(STORE,{keyPath:'id'});};r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);});}
window.probeWrite=async tag=>{localStorage.setItem(KEY,tag);const d=await db();await new Promise((res,rej)=>{const t=d.transaction(STORE,'readwrite');t.objectStore(STORE).put({id:'sentinel',tag});t.oncomplete=res;t.onerror=()=>rej(t.error);});d.close();const c=await caches.open(CACHE);await c.put('/__origin_probe_sentinel__',new Response(tag));const reg=await navigator.serviceWorker.register('/origin-probe-sw.js',{scope:'/'});await navigator.serviceWorker.ready;return {origin:location.origin,scope:reg.scope,script:reg.active?.scriptURL||reg.installing?.scriptURL||reg.waiting?.scriptURL||null};};
window.probeRead=async()=>{let idb=null;try{const d=await db();idb=await req(d.transaction(STORE).objectStore(STORE).get('sentinel'));d.close();}catch(e){}const c=await caches.open(CACHE);const cr=await c.match('/__origin_probe_sentinel__');const regs=await navigator.serviceWorker.getRegistrations();return {origin:location.origin,path:location.pathname,local:localStorage.getItem(KEY),idb:idb&&idb.tag||null,cache:cr?await cr.text():null,registrations:regs.map(r=>({scope:r.scope,script:r.active?.scriptURL||r.installing?.scriptURL||r.waiting?.scriptURL||null}))};};
window.probeClear=async()=>{localStorage.removeItem(KEY);await caches.delete(CACHE);for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();await new Promise(res=>{const r=indexedDB.deleteDatabase(DB);r.onsuccess=r.onerror=r.onblocked=()=>res();});return true;};
</script>`;
const sw=`self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',()=>{});`;
function server(port){const s=http.createServer((q,r)=>{if(q.url==='/origin-probe-sw.js'){r.writeHead(200,{'content-type':'application/javascript','service-worker-allowed':'/','cache-control':'no-store'});r.end(sw);return;}r.writeHead(200,{'content-type':'text/html','cache-control':'no-store'});r.end(html);});return new Promise((res,rej)=>{s.listen(port,'127.0.0.1',()=>res(s));s.on('error',rej);});}
const ok=(c,m)=>{if(!c)throw new Error(m);},out={schema:'ldc-e16-e19-origin-isolation-qa-v1',checks:{},details:{},status:'UNKNOWN'};
const s1=await server(8821),s2=await server(8822);let b;
try{
 b=await chromium.launch({headless:true});const ctx=await b.newContext();
 const a=await ctx.newPage(),x=await ctx.newPage(),same=await ctx.newPage();
 await a.goto('http://127.0.0.1:8821/path-a/');await x.goto('http://127.0.0.1:8822/ldc/');await same.goto('http://127.0.0.1:8821/path-b/');
 await Promise.all([a.evaluate(()=>probeClear()),x.evaluate(()=>probeClear())]);
 const wa=await a.evaluate(()=>probeWrite('ORIGIN_A'));const before=await x.evaluate(()=>probeRead());
 out.details.cross_before=before;out.checks.origins_differ=wa.origin!==before.origin;
 out.checks.cross_origin_starts_isolated=before.local===null&&before.idb===null&&before.cache===null&&before.registrations.length===0;
 const wx=await x.evaluate(()=>probeWrite('ORIGIN_B'));const ar=await a.evaluate(()=>probeRead()),xr=await x.evaluate(()=>probeRead());
 out.details.cross_after={a:ar,b:xr};
 out.checks.indexeddb_isolated=ar.idb==='ORIGIN_A'&&xr.idb==='ORIGIN_B';
 out.checks.localstorage_isolated=ar.local==='ORIGIN_A'&&xr.local==='ORIGIN_B';
 out.checks_cache=ar.cache==='ORIGIN_A'&&xr.cache==='ORIGIN_B';out.checks.cache_storage_isolated=out.checks_cache;delete out.checks_cache;
 out.checks.service_workers_origin_isolated=ar.registrations.length===1&&xr.registrations.length===1&&new URL(ar.registrations[0].scope).origin===ar.origin&&new URL(xr.registrations[0].scope).origin===xr.origin&&new URL(ar.registrations[0].script).origin===ar.origin&&new URL(xr.registrations[0].script).origin===xr.origin;
 await a.evaluate(()=>probeWrite('SAME_ORIGIN_PATH_A'));const sr=await same.evaluate(()=>probeRead());out.details.same_origin_path_control=sr;
 out.checks.pathname_does_not_isolate=sr.local==='SAME_ORIGIN_PATH_A'&&sr.idb==='SAME_ORIGIN_PATH_A'&&sr.cache==='SAME_ORIGIN_PATH_A';
 out.checks.same_origin_control_confirmed=sr.origin===wa.origin&&sr.path!==ar.path;
 out.status=Object.values(out.checks).every(Boolean)?'PASS':'FAIL';
 await Promise.all([a.evaluate(()=>probeClear()),x.evaluate(()=>probeClear())]);
}finally{if(b)await b.close();await Promise.all([new Promise(r=>s1.close(r)),new Promise(r=>s2.close(r))]);}
fs.writeFileSync('wip-e16-e19-origin-isolation-qa.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));if(out.status!=='PASS')process.exitCode=1;
