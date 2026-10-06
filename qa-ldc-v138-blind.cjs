const {chromium}=require('playwright');
const fs=require('fs'),crypto=require('crypto'),path=require('path');
const URL='http://127.0.0.1:8122/ldc-v138-fullqa-corrective/';
const EXPECT={app:'v2.19.138-R1B-UX-ACCESS-R11',pub:'138',sw:'ldc-v2.19.138-R1B-ux-access-r11'};
const out={candidate:'LDC v138/R11 independent blind challenge',generated_at:new Date().toISOString(),overall:'UNKNOWN'};
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
   await goSearch();const si=document.getElementById('search-input');si.value='bateau';await runSearch();for(let n=0;n<100;n++){if(document.getElementById('search-meta')?.textContent!=='Recherche…')break;await new Promise(r=>setTimeout(r,100));}const searchMeta=document.getElementById('search-meta')?.textContent||'';
   await openHelp();document.documentElement.setAttribute('data-theme','dark');const tip=document.querySelector('.help-tip'),sum=document.querySelector('.provenance-details>summary'),secondary=document.getElementById('help-provenance-cta');const vis=e=>!!e&&getComputedStyle(e).display!=='none';
   const parse=s=>{const m=String(s).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);return m?[+m[1],+m[2],+m[3]]:null};const lum=a=>a.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((z,v,i)=>z+v*[.2126,.7152,.0722][i],0);const ratio=e=>{const cs=getComputedStyle(e),fg=parse(cs.color),bg=parse(cs.backgroundColor);if(!fg||!bg)return null;const a=lum(fg),b=lum(bg);return{fg:cs.color,bg:cs.backgroundColor,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)}};const css=[tip,sum].filter(Boolean).map(e=>({tag:e.tagName,fg:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor}));const secondaryContrast=secondary?ratio(secondary):null;
   return{app:APP_VERSION,pub:PUBLIC_VERSION,swExpected:SW_CACHE_VERSION,build:APP_BUILD,versionApp:version.app_version,versionPub:version.public_version,versionWorker:version.page_worker_revision,offlineApp:offline.app_version,offlineWorker:offline.page_worker_revision,searchMeta,searchFailed:/indisponible/i.test(searchMeta),secondaryContrast,swHasVersion:sw.includes("const VERSION = 'ldc-v2.19.138-R1B-ux-access-r11'"),swHasShell:sw.includes('shell-v2.19.138-R1B-ux-access-r11'),swHasRuntime:sw.includes('runtime-v2.19.138-R1B-ux-access-r11'),swHasStale:/shell-v2\.19\.(135|136|137)|runtime-v2\.19\.(135|136|137)/.test(sw),caches:keys,tomes,entries,loadingVisible:vis(document.getElementById('loading')),versionPill:document.getElementById('version-pill-home')?.textContent||'',css};
 });
 const local=fs.readFileSync(path.join(process.cwd(),'ldc-v138-fullqa-corrective','index.html'));out.index={served:sha(Buffer.from(await r.body())),local:sha(local)};
 out.errors={page:errors,console:consoleErrors};
 const pz=out.probes,hasCaches=pz.caches.some(x=>/shell-v2\.19\.137-R1B-ux-access-r10$/.test(x))&&pz.caches.some(x=>/runtime-v2\.19\.137-R1B-ux-access-r10$/.test(x)),staleCaches=pz.caches.filter(x=>/shell-v2\.19\.(135|136|137)|runtime-v2\.19\.(135|136|137)/.test(x));
 out.falsification={servedExact:out.index.served===out.index.local,identity:pz.app===EXPECT.app&&pz.pub===EXPECT.pub&&pz.swExpected===EXPECT.sw&&pz.versionApp===EXPECT.app&&pz.versionPub===EXPECT.pub&&pz.versionWorker===EXPECT.sw&&pz.offlineApp===EXPECT.app&&pz.offlineWorker===EXPECT.sw,workerText:pz.swHasVersion&&pz.swHasShell&&pz.swHasRuntime&&!pz.swHasStale,caches:hasCaches&&staleCaches.length===0,ready:!pz.loadingVisible&&pz.versionPill==='v138',navigation:pz.tomes===36&&pz.entries>0,search:!pz.searchFailed,contrast:!!pz.secondaryContrast&&pz.secondaryContrast.ratio>=4.5,build:pz.build==='2026-10-04',noErrors:errors.length===0&&consoleErrors.length===0};
 out.falsification.staleCaches=staleCaches;
 out.overall=Object.entries(out.falsification).filter(([k])=>k!=='staleCaches').every(([,v])=>v===true)?'PASS':'FAIL';
 await c.close();
}
run().catch(e=>{out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}).finally(()=>{fs.writeFileSync('qa-ldc-v138-blind-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({overall:out.overall,falsification:out.falsification,probes:out.probes&&{app:out.probes.app,caches:out.probes.caches,tomes:out.probes.tomes,entries:out.probes.entries}},null,2));});
