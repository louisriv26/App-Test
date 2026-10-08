import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';import {chromium} from 'playwright';
const P='7c292d6221bb350fac3aeaa83750b8784706d45c',ROOT='/tmp/ldc-r23-root',LIVE='/tmp/ldc-r23-live',URL='http://127.0.0.1:8999/',ART='LDC_v142.19_R27_BLOCKED_MULTITAB_USER_REPAIR_DIAGNOSTIC.json';
const pack=JSON.parse(fs.readFileSync('LDC_v142.19_GEOMETRY_CANDIDATE_PACKAGE_AUDIT.json'));const out={schema:'R27_READ_ONLY_MULTITAB_USER_RECOVERY_ADVERSARIAL',tested_at:new Date().toISOString(),tests:[],errors:[],mutation_authority:'NONE',status:'NOT_RUN'};
function stage(label,old=false){const dir=path.join(ROOT,label);for(const x of pack.entries){let target=path.join(dir,x.path);fs.mkdirSync(path.dirname(target),{recursive:true});if(old&&['index.html','sw.js','version.json','offline_manifest.json'].includes(x.path))fs.writeFileSync(target,execFileSync('git',['show',P+':'+x.path],{maxBuffer:8*1024*1024}));else fs.linkSync(path.resolve(x.path),target);}return dir;}
function select(p){try{fs.unlinkSync(LIVE+'.new')}catch(_){}fs.symlinkSync(p,LIVE+'.new','dir');fs.renameSync(LIVE+'.new',LIVE);}
async function workers(page){return page.evaluate(async()=>{
 let regs=await navigator.serviceWorker.getRegistrations();const ss=await Promise.all(regs.map(async r=>{
 const versions={};for(const [name,w] of [['active',r.active],['waiting',r.waiting],['installing',r.installing]])if(w){versions[name]={url:w.scriptURL,state:w.state,reported:await new Promise(resolve=>{const ch=new MessageChannel(),t=setTimeout(()=>resolve('timeout'),1200);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data?.version||JSON.stringify(e.data).slice(0,200))};try{w.postMessage({type:'LDC_GET_VERSION'},[ch.port2])}catch(e){clearTimeout(t);resolve(String(e))}})}}
 return{scope:r.scope,workerVersions:versions}}));return{regs:ss,controller:!!navigator.serviceWorker.controller,ready:document.getElementById('loading')?.style?.display,bootStage:typeof bootStage==='string'?bootStage:null,loading:document.querySelector('#loading')?.innerText.slice(0,400),publicVersion:typeof PUBLIC_VERSION!=='undefined'?PUBLIC_VERSION:null}});
}
let browser;
try{
 const old=stage('old',true),current=stage('new',false);select(old);
 browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 for(const multiple of [false,true]){
  select(old);
  const cx=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844}}),tab=await cx.newPage();
  const t={scenario:multiple?'predecessor_two_tabs_then_update':'predecessor_single_tab_then_update',swEvents:[],pageErrors:[],checks:{}};out.tests.push(t);
  tab.on('console',m=>{if(m.type()==='error')t.pageErrors.push(m.text().slice(0,300))});
  const cdps=await cx.newCDPSession(tab);await cdps.send('ServiceWorker.enable');
  for(const event of ['workerErrorReported','workerVersionUpdated','registrationUpdated'])cdps.on('ServiceWorker.'+event,d=>t.swEvents.push({event,detail:JSON.stringify(d).slice(0,4000)}));
  let second=null;
  try{
   await tab.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});
   await tab.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:100000});
   const seed=await tab.evaluate(async()=>{await navigator.serviceWorker.ready;await dbPut('settings',{key:'__R23_SYNTHETIC_ONLY',val:'PRESERVE'});return (await dbGetAll('settings')).find(x=>x.key==='__R23_SYNTHETIC_ONLY')?.val});
   t.seed_ok=seed==='PRESERVE';t.originalWorkers=await workers(tab);
   if(multiple){second=await cx.newPage();await second.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});await second.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:100000});}
   select(current);
   t.newPublishedSW=(await tab.evaluate(async()=>({script:(await(await fetch('sw.js',{cache:'no-store'})).text()).slice(0,145),version:(await(await fetch('version.json',{cache:'no-store'})).json()).app_version})));
   // Preemptively request an update while the predecessor UI is still running.
   t.manualUpdate = await tab.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();try{await r.update();return{status:'resolved',installing:r.installing?.state,waiting:r.waiting?.state,active:r.active?.state}}catch(e){return{status:'rejected',error:String(e),stack:String(e.stack).slice(0,500)}}});
   await tab.waitForTimeout(8500);t.postManualWorkers=await workers(tab);
   const next=await cx.newPage();next.on('console',m=>{if(m.type()==='error')t.pageErrors.push('NEW:'+m.text().slice(0,350))});
   await next.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});
   const bootok=await next.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:28000}).then(()=>true).catch(()=>false);
   t.newBootCompleted=bootok;t.newWorkers=await workers(next);
   t.syntheticStillPresent=await next.evaluate(async()=>{try{return (await dbGetAll('settings')).some(x=>x.key==='__R23_SYNTHETIC_ONLY'&&x.val==='PRESERVE')}catch(e){return 'READ_ERROR:'+String(e)}}).catch(e=>'EVALUATION_ERROR:'+String(e));
   if(!bootok){
     let btn=next.locator('#boot-repair-btn');t.repair_button_visible=await btn.isVisible().catch(()=>false);
     if(t.repair_button_visible){
       try{
         await btn.click({timeout:12000});
         t.user_facing_repair_recovered=await next.waitForFunction(()=>{let l=document.getElementById('loading');return l&&getComputedStyle(l).display==='none'&&typeof PUBLIC_VERSION==='string'&&PUBLIC_VERSION==='142.19'},null,{timeout:70000}).then(()=>true).catch(()=>false);
         t.user_facing_repair_state=await workers(next);
         t.user_facing_repair_kept_data=await next.evaluate(async()=>{try{return(await dbGetAll('settings')).some(x=>x.key==='__R23_SYNTHETIC_ONLY'&&x.val==='PRESERVE')}catch(e){return 'NO_DB:'+String(e)}});
       }catch(er){t.user_facing_repair_error=String(er)}
     }
   }
   t.pass=(bootok&&t.syntheticStillPresent===true)||(t.user_facing_repair_recovered===true&&t.user_facing_repair_kept_data===true);
   await next.close();
  }catch(e){t.errors=[String(e?.stack||e)];t.pass=false}
  finally{if(second)await second.close().catch(()=>{});await cx.close().catch(()=>{})}
 }
 out.status=out.tests.every(t=>t.pass)?'PASS_SCOPED_SYNTHETIC_SAME_ROOT_OLD_TO_NEW':'FAIL_SCOPED_SYNTHETIC_UPGRADE_OR_TEST';
}catch(e){out.errors.push(String(e));out.status='ERROR'}
finally{fs.writeFileSync(ART,JSON.stringify(out,null,2)+'\n');if(browser)await browser.close().catch(()=>{});console.log(JSON.stringify({status:out.status,scenarios:out.tests.map(t=>({name:t.scenario,pass:t.pass,boot:t.newBootCompleted,manual:t.manualUpdate,swErrors:t.swEvents.filter(e=>e.event==='workerErrorReported').slice(0,4)}))},null,2))}
