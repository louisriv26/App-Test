const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.join(process.cwd(),'ldc-v137-r10-release-integrity');
const URL='http://127.0.0.1:8120/ldc-v137-r10-release-integrity/';
const PROFILE=path.join(process.cwd(),'.qa-ldc-v137-profile');
const EXPECT={app:'v2.19.137-R1B-UX-ACCESS-R10',pub:'137',sw:'ldc-v2.19.137-R1B-ux-access-r10',tree:'44f92a8aaedb8ab0ef3f689751a31715e8813868'};
const out={candidate:'LDC v137/R10',generated_at:new Date().toISOString(),overall:'UNKNOWN'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitReady(p,timeout=90000){
  await p.waitForFunction(()=>{const l=document.getElementById('loading');const vp=document.getElementById('version-pill-home');return l&&getComputedStyle(l).display==='none'&&vp&&vp.textContent&&!/v—|v-$/.test(vp.textContent);},{timeout});
}
async function workerVersion(p){
  return p.evaluate(()=>new Promise(resolve=>{
    const w=navigator.serviceWorker.controller;
    if(!w)return resolve(null);
    const ch=new MessageChannel(),t=setTimeout(()=>resolve(null),5000);
    ch.port1.onmessage=e=>{clearTimeout(t);resolve(e&&e.data&&e.data.version||null);};
    try{w.postMessage({type:'LDC_GET_VERSION'},[ch.port2]);}catch(_){clearTimeout(t);resolve(null);}
  }));
}
async function swState(p){
  return p.evaluate(async()=>{
    const reg=await navigator.serviceWorker.ready;
    return {controller:!!navigator.serviceWorker.controller,active:reg.active&&reg.active.scriptURL,waiting:!!reg.waiting,installing:!!reg.installing,caches:(await caches.keys()).filter(x=>x.startsWith('ldc-le-livre-du-ciel-')).sort()};
  });
}
function contrast(fg,bg){
  const parse=s=>{const m=String(s).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);return m?[+m[1],+m[2],+m[3]]:null};
  const lum=a=>a.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((z,v,i)=>z+v*[.2126,.7152,.0722][i],0);
  const a=lum(parse(fg)),b=lum(parse(bg));return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
}
async function run(){
 fs.rmSync(PROFILE,{recursive:true,force:true});
 const c=await chromium.launchPersistentContext(PROFILE,{headless:true,serviceWorkers:'allow',viewport:{width:1180,height:850}});
 const p=await c.newPage(),errors=[],consoleErrors=[];
 p.on('pageerror',e=>errors.push(String(e)));
 p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 const r=await p.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});
 out.navigation={status:r.status(),sha256:sha(Buffer.from(await r.body())),expected:sha(fs.readFileSync(path.join(ROOT,'index.html')))};
 await waitReady(p);
 let s=await swState(p);
 if(!s.controller){await p.reload({waitUntil:'domcontentloaded',timeout:90000});await waitReady(p);s=await swState(p);}
 out.identity=await p.evaluate(async()=>({app:APP_VERSION,pub:PUBLIC_VERSION,swExpected:SW_CACHE_VERSION,versionPill:document.getElementById('version-pill-home')?.textContent||'',loadingVisible:getComputedStyle(document.getElementById('loading')).display!=='none',published:await fetch('./version.json',{cache:'no-store'}).then(r=>r.json())}));
 out.worker_version=await workerVersion(p);out.sw=s;
 out.cache_binding={has137Shell:s.caches.some(x=>/shell-v2\.19\.137-R1B-ux-access-r10$/.test(x)),has137Runtime:s.caches.some(x=>/runtime-v2\.19\.137-R1B-ux-access-r10$/.test(x)),stale:s.caches.filter(x=>/shell-v2\.19\.(135|136)|runtime-v2\.19\.(135|136)/.test(x))};
 out.journeys=await p.evaluate(async()=>{
   const q={};
   await goTomes();q.tomes={count:document.querySelectorAll('#tomes-list .vol-card').length,label:document.getElementById('tomes-count')?.textContent||''};
   await openTome(1,{intent:NAV_INTENT.FRESH_TOME});q.tome1={entries:document.querySelectorAll('#entries-list .entry-item').length,title:document.getElementById('entries-title')?.textContent||''};
   await goSearch();const i=document.getElementById('search-input');i.value='bateau';await runSearch();
   for(let n=0;n<100;n++){if(document.getElementById('search-meta')?.textContent!=='Recherche…')break;await new Promise(r=>setTimeout(r,100));}
   q.search={meta:document.getElementById('search-meta')?.textContent||'',cards:document.querySelectorAll('#search-results .search-card').length,failed:/indisponible/i.test(document.getElementById('search-meta')?.textContent||'')};
   await openHelp();const hs=document.getElementById('help-scroll');hs.scrollTop=Math.min(500,Math.max(0,hs.scrollHeight-hs.clientHeight));const before=hs.scrollTop;await openProvenanceDetails('help');await new Promise(r=>setTimeout(r,250));const provTop=document.getElementById('provenance-scroll')?.scrollTop||0;await closeProvenanceDetails();await new Promise(r=>setTimeout(r,350));const after=hs.scrollTop;
   q.helpProvenance={before,provTop,after,restored:Math.abs(after-before)<=3&&Math.abs(provTop)<=1};
   return q;
 });
 out.dark=await p.evaluate(()=>{
   document.documentElement.setAttribute('data-theme','dark');
   const ids=['resume-reading-btn','help-provenance-cta'];
   const vals={};
   const parse=s=>{const m=String(s).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);return m?[+m[1],+m[2],+m[3]]:null};
   const lum=a=>a.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((z,v,i)=>z+v*[.2126,.7152,.0722][i],0);
   for(const id of ids){const e=document.getElementById(id);if(!e)continue;const cs=getComputedStyle(e),fg=parse(cs.color),bg=parse(cs.backgroundColor);if(fg&&bg){const a=lum(fg),b=lum(bg);vals[id]={fg:cs.color,bg:cs.backgroundColor,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};}}
   return vals;
 });
 out.backup_roundtrip=await p.evaluate(async()=>{
   const wait=ms=>new Promise(r=>setTimeout(r,ms));
   await setThemePreference('dark');await wait(150);
   const env=await collectUserDataEnvelope();await setThemePreference('light');await wait(100);
   const prepared=await prepareBackupEnvelopeForImport(env),bytes=new TextEncoder().encode(JSON.stringify(prepared.env)).length,validation=await validateBackupEnvelope(prepared.env,bytes);
   if(!validation.ok)return{pass:false,errors:validation.errors};
   pendingBackupImport={kind:'legacy-json',env:prepared.env,validation,fileName:'qa-v137.json',migrationSummary:prepared.summary};await confirmImportBackup();
   let theme=null;for(let n=0;n<30;n++){theme=await dbGet('settings','theme').catch(()=>null);if(theme&&theme.val==='dark')break;await wait(100);}
   return{pass:!!theme&&theme.val==='dark',theme:theme&&theme.val,warnings:validation.warnings||[]};
 });
 await p.evaluate(()=>{window.__qaD11=[];const live=document.getElementById('offline-at-status'),toast=document.getElementById('toast');const take=()=>window.__qaD11.push({live:live?.textContent||'',toast:toast?.textContent||'',state:offlineUiState?.state||null});if(live)new MutationObserver(take).observe(live,{subtree:true,childList:true,characterData:true});if(toast)new MutationObserver(take).observe(toast,{subtree:true,childList:true,characterData:true});take();});
 await p.evaluate(()=>startOfflinePreparation());
 try{await p.waitForFunction(()=>typeof offlineUiState!=='undefined'&&['READY','ERROR','PARTIAL','CANCELLED'].includes(offlineUiState.state),{timeout:300000,polling:1000});}catch(e){out.offline_wait_error=String(e);}
 out.offline=await p.evaluate(async()=>{const saved=await dbGet('settings','offline_completion').catch(()=>null);return{state:offlineUiState.state,completed:offlineUiState.completed,total:offlineUiState.total,failed:(offlineUiState.failed||[]).length,total_bytes:offlineUiState.total_bytes,label:document.getElementById('offline-state-label')?.textContent||'',saved:saved&&(saved.val||saved.value),events:window.__qaD11||[]};});
 out.offline.pass=out.offline.state==='READY'&&out.offline.completed===204&&out.offline.total===204&&out.offline.failed===0&&out.offline.saved&&out.offline.saved.state==='READY';
 out.errors={page:errors,console:consoleErrors};
 await c.close();
 const c2=await chromium.launchPersistentContext(PROFILE,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});
 await c2.setOffline(true);const p2=await c2.newPage(),offErrors=[];p2.on('pageerror',e=>offErrors.push(String(e)));
 let nav=true,navError=null;try{await p2.goto(URL,{waitUntil:'domcontentloaded',timeout:60000});await waitReady(p2,60000);}catch(e){nav=false;navError=String(e);}
 out.cold=await p2.evaluate(async()=>{async function f(u){try{const r=await fetch(u,{cache:'no-store'}),b=await r.arrayBuffer();return{ok:r.ok,status:r.status,bytes:b.byteLength}}catch(e){return{ok:false,error:String(e)}}}return{app:APP_VERSION,pub:PUBLIC_VERSION,pill:document.getElementById('version-pill-home')?.textContent||'',loadingVisible:getComputedStyle(document.getElementById('loading')).display!=='none',saved:(await dbGet('settings','offline_completion').catch(()=>null))?.val||null,volume36:await f('./corpus/volume_36.json'),searchIndex:await f('./corpus/search_v2_index.json')};});
 out.cold.nav=nav;out.cold.navError=navError;out.cold.errors=offErrors;
 out.cold.pass=nav&&out.cold.app===EXPECT.app&&out.cold.pub===EXPECT.pub&&!out.cold.loadingVisible&&out.cold.saved&&out.cold.saved.state==='READY'&&out.cold.volume36.ok&&out.cold.searchIndex.ok;
 await c2.close();
 const darkPass=Object.values(out.dark).length>=2&&Object.values(out.dark).every(x=>x.ratio>=4.5);
 const journeyPass=out.journeys.tomes.count===36&&out.journeys.tome1.entries>0&&!out.journeys.search.failed&&out.journeys.helpProvenance.restored;
 out.overall=out.navigation.status===200&&out.navigation.sha256===out.navigation.expected&&out.identity.app===EXPECT.app&&out.identity.pub===EXPECT.pub&&out.identity.swExpected===EXPECT.sw&&out.identity.published.app_version===EXPECT.app&&out.identity.published.public_version===EXPECT.pub&&!out.identity.loadingVisible&&out.worker_version===EXPECT.sw&&out.sw.controller&&out.cache_binding.has137Shell&&out.cache_binding.has137Runtime&&out.cache_binding.stale.length===0&&journeyPass&&darkPass&&out.backup_roundtrip.pass&&out.offline.pass&&out.cold.pass&&errors.length===0&&consoleErrors.length===0?'PASS':'FAIL';
}
run().catch(e=>{out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}).finally(()=>{fs.writeFileSync('qa-ldc-v137-current-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({overall:out.overall,identity:out.identity,cache_binding:out.cache_binding,journeys:out.journeys,offline:out.offline&&{state:out.offline.state,completed:out.offline.completed,total:out.offline.total,failed:out.offline.failed,pass:out.offline.pass},cold:out.cold&&{pass:out.cold.pass}},null,2));});
