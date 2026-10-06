const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const SERVE=path.join(process.cwd(),'qa-ldc-v139-upgrade'),APP=path.join(SERVE,'app'),PROFILE=path.join(process.cwd(),'.qa-ldc-v139-upgrade-profile');
const URL='http://127.0.0.1:8131/app/',EXPECT={app:'v2.19.139-R1B-UX-ACCESS-R12',pub:'139',sw:'ldc-v2.19.139-R1B-ux-access-r12'};
const out={candidate:'LDC v139/R12 predecessor upgrade',generated_at:new Date().toISOString(),overall:'UNKNOWN'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
async function ready(p,t=90000){await p.waitForFunction(()=>{const l=document.getElementById('loading'),vp=document.getElementById('version-pill-home');return l&&getComputedStyle(l).display==='none'&&vp&&vp.textContent&&!/v—|v-$/.test(vp.textContent);},{timeout:t});}
async function snap(p){return p.evaluate(async()=>({app:APP_VERSION,pub:PUBLIC_VERSION,swExpected:SW_CACHE_VERSION,controller:!!navigator.serviceWorker.controller,caches:(await caches.keys()).filter(x=>x.startsWith('ldc-le-livre-du-ciel-')).sort(),pill:document.getElementById('version-pill-home')?.textContent||'',loadingVisible:getComputedStyle(document.getElementById('loading')).display!=='none',local:localStorage.getItem('qa_v139_local'),idb:(await dbGet('settings','qa_v139_sentinel').catch(()=>null))?.val||null,version:await fetch('./version.json',{cache:'no-store'}).then(r=>r.json())}));}
async function run(){
 fs.rmSync(PROFILE,{recursive:true,force:true});fs.mkdirSync(SERVE,{recursive:true});copy(path.join(process.cwd(),'ldc-v138-fullqa-corrective'),APP);
 const c=await chromium.launchPersistentContext(PROFILE,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});
 const p=await c.newPage(),errors=[],consoleErrors=[];p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 await p.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});await ready(p);
 let reg=await p.evaluate(()=>navigator.serviceWorker.ready.then(r=>({controller:!!navigator.serviceWorker.controller,active:!!r.active})));
 if(!reg.controller){await p.reload({waitUntil:'domcontentloaded',timeout:90000});await ready(p);}
 await p.evaluate(async()=>{localStorage.setItem('qa_v139_local','keep-v139');await dbPut('settings',{key:'qa_v139_sentinel',val:'keep-v139',ts:Date.now()});});
 out.pre=await snap(p);
 copy(path.join(process.cwd(),'ldc-v139-r12-search-v21a-recert'),APP);
 const activation=await p.evaluate(async()=>{
   const reg=await navigator.serviceWorker.getRegistration();if(!reg)throw new Error('no_registration');
   let changes=0;navigator.serviceWorker.addEventListener('controllerchange',()=>changes++);
   await reg.update();
   const end=Date.now()+30000;while(Date.now()<end&&!reg.waiting){if(reg.installing)await new Promise(r=>setTimeout(r,200));else await new Promise(r=>setTimeout(r,200));}
   if(reg.waiting)reg.waiting.postMessage({type:'SKIP_WAITING'});
   const end2=Date.now()+30000;while(Date.now()<end2&&changes===0)await new Promise(r=>setTimeout(r,200));
   return{waiting:!!reg.waiting,installing:!!reg.installing,controllerChanges:changes};
 });
 out.activation=activation;
 await p.reload({waitUntil:'domcontentloaded',timeout:90000});await ready(p);
 out.post=await snap(p);
 out.search=await p.evaluate(async()=>{await goSearch();const samples={};for(const term of ['bateau','de','je','volonte\u0301']){const i=document.getElementById('search-input');i.value=term;await runSearch();for(let n=0;n<150;n++){if(document.getElementById('search-meta')?.textContent!=='Recherche…')break;await new Promise(r=>setTimeout(r,100));}const meta=document.getElementById('search-meta')?.textContent||'',cards=document.querySelectorAll('#search-results .result-card, #search-results .search-card').length;samples[term]={meta,failed:/indisponible/i.test(meta),cards};}return{samples,failed:Object.values(samples).some(x=>x.failed||x.cards===0)};});
 out.online_post_errors={page:errors,console:consoleErrors};
 await c.setOffline(true);let offlineNav=true,offlineError=null;try{await p.reload({waitUntil:'domcontentloaded',timeout:60000});await ready(p,60000);}catch(e){offlineNav=false;offlineError=String(e);}
 out.offline=await snap(p);out.offline.nav=offlineNav;out.offline.error=offlineError;
 const has139=out.post.caches.some(x=>/shell-v2\.19\.139-R1B-ux-access-r12$/.test(x))&&out.post.caches.some(x=>/runtime-v2\.19\.139-R1B-ux-access-r12$/.test(x));
 const stale=out.post.caches.filter(x=>/shell-v2\.19\.(135|136|137|138)|runtime-v2\.19\.(135|136|137|138)/.test(x));
 out.assertions={pre138:out.pre.app==='v2.19.138-R1B-UX-ACCESS-R11'&&out.pre.pub==='138',post139:out.post.app===EXPECT.app&&out.post.pub===EXPECT.pub&&out.post.swExpected===EXPECT.sw&&out.post.version.app_version===EXPECT.app&&!out.post.loadingVisible,cache139:has139,staleRemoved:stale.length===0,statePreserved:out.post.local==='keep-v139'&&out.post.idb==='keep-v139',searchWorks:out.search&&!out.search.failed,offline139:offlineNav&&out.offline.app===EXPECT.app&&out.offline.pub===EXPECT.pub&&!out.offline.loadingVisible&&out.offline.local==='keep-v139'&&out.offline.idb==='keep-v139',noErrors:errors.length===0&&consoleErrors.length===0};
 out.assertions.stale=stale;
 out.overall=Object.entries(out.assertions).filter(([k])=>k!=='stale').every(([,v])=>v===true)?'PASS':'FAIL';
 await c.close();
}
run().catch(e=>{out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}).finally(()=>{fs.writeFileSync('qa-ldc-v139-update-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({overall:out.overall,pre:out.pre&&{app:out.pre.app,caches:out.pre.caches},post:out.post&&{app:out.post.app,caches:out.post.caches},assertions:out.assertions},null,2));});
