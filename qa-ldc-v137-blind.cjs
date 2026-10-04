const {chromium}=require('playwright');
const fs=require('fs'),crypto=require('crypto'),path=require('path');
const URL='http://127.0.0.1:8122/ldc-v137-r10-release-integrity/';
const EXPECT={app:'v2.19.137-R1B-UX-ACCESS-R10',pub:'137',sw:'ldc-v2.19.137-R1B-ux-access-r10'};
const out={candidate:'LDC v137/R10 independent blind challenge',generated_at:new Date().toISOString(),overall:'UNKNOWN'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function run(){
 const c=await chromium.launch({headless:true});const ctx=await c.newContext({viewport:{width:1024,height:768},serviceWorkers:'allow'});const p=await ctx.newPage(),errors=[],consoleErrors=[];
 p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 const r=await p.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});
 await p.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',{timeout:90000});
 await p.waitForFunction(()=>navigator.serviceWorker.ready.then(()=>true),{timeout:30000});
 if(!await p.evaluate(()=>!!navigator.serviceWorker.controller)){await p.reload({waitUntil:'domcontentloaded',timeout:90000});await p.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',{timeout:90000});}
 out.probes=await p.evaluate(async()=>{
   const version=await fetch('./version.json',{cache:'no-store'}).then(r=>r.json()),offline=await fetch('./offline_manifest.json',{cache:'no-store'}).then(r=>r.json()),sw=await fetch('./sw.js',{cache:'no-store'}).then(r=>r.text()),keys=(await caches.keys()).filter(x=>x.startsWith('ldc-le-livre-du-ciel-')).sort();
   await goTomes();const tomes=document.querySelectorAll('#tomes-list .vol-card').length;await openTome(36,{intent:NAV_INTENT.FRESH_TOME});const entries=document.querySelectorAll('#entries-list .entry-item').length;
   await openHelp();document.documentElement.setAttribute('data-theme','dark');const tip=document.querySelector('.help-tip'),sum=document.querySelector('.provenance-details>summary');const vis=e=>!!e&&getComputedStyle(e).display!=='none';
   const css=[tip,sum].filter(Boolean).map(e=>({tag:e.tagName,fg:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor}));
   return{app:APP_VERSION,pub:PUBLIC_VERSION,swExpected:SW_CACHE_VERSION,versionApp:version.app_version,versionPub:version.public_version,versionWorker:version.page_worker_revision,offlineApp:offline.app_version,offlineWorker:offline.page_worker_revision,swHasVersion:sw.includes("const VERSION = 'ldc-v2.19.137-R1B-ux-access-r10'"),swHasShell:sw.includes('shell-v2.19.137-R1B-ux-access-r10'),swHasRuntime:sw.includes('runtime-v2.19.137-R1B-ux-access-r10'),swHasStale:/shell-v2\.19\.(135|136)|runtime-v2\.19\.(135|136)/.test(sw),caches:keys,tomes,entries,loadingVisible:vis(document.getElementById('loading')),versionPill:document.getElementById('version-pill-home')?.textContent||'',css};
 });
 const local=fs.readFileSync(path.join(process.cwd(),'ldc-v137-r10-release-integrity','index.html'));out.index={served:sha(Buffer.from(await r.body())),local:sha(local)};
 out.errors={page:errors,console:consoleErrors};
 const pz=out.probes,hasCaches=pz.caches.some(x=>/shell-v2\.19\.137-R1B-ux-access-r10$/.test(x))&&pz.caches.some(x=>/runtime-v2\.19\.137-R1B-ux-access-r10$/.test(x)),staleCaches=pz.caches.filter(x=>/shell-v2\.19\.(135|136)|runtime-v2\.19\.(135|136)/.test(x));
 out.falsification={servedExact:out.index.served===out.index.local,identity:pz.app===EXPECT.app&&pz.pub===EXPECT.pub&&pz.swExpected===EXPECT.sw&&pz.versionApp===EXPECT.app&&pz.versionPub===EXPECT.pub&&pz.versionWorker===EXPECT.sw&&pz.offlineApp===EXPECT.app&&pz.offlineWorker===EXPECT.sw,workerText:pz.swHasVersion&&pz.swHasShell&&pz.swHasRuntime&&!pz.swHasStale,caches:hasCaches&&staleCaches.length===0,ready:!pz.loadingVisible&&pz.versionPill==='v137',navigation:pz.tomes===36&&pz.entries>0,noErrors:errors.length===0&&consoleErrors.length===0};
 out.falsification.staleCaches=staleCaches;
 out.overall=Object.entries(out.falsification).filter(([k])=>k!=='staleCaches').every(([,v])=>v===true)?'PASS':'FAIL';
 await c.close();
}
run().catch(e=>{out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}).finally(()=>{fs.writeFileSync('qa-ldc-v137-blind-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({overall:out.overall,falsification:out.falsification,probes:out.probes&&{app:out.probes.app,caches:out.probes.caches,tomes:out.probes.tomes,entries:out.probes.entries}},null,2));});
