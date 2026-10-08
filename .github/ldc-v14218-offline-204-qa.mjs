import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const port=8951, base='http://127.0.0.1:'+port;
const report={schema:'ldc-v14218-204-resource-real-offline-browser-v1',
 source_sha:process.env.GITHUB_SHA||null,status:'NOT_EXECUTED',checks:{},details:{},errors:[],
 evidence_scope:'FRESH LOCAL CHROMIUM PROFILE ONLY; NOT LIVE ORIGIN, NOT PHYSICAL SAFARI',
 deployment_authority:'NONE',app_test_hosted_gate:'OPEN',physical_device_gate:'OPEN'};
const verify=(name,ok,detail)=>{report.checks[name]=!!ok;report.details[name]=detail;};
let browser,server;
try{
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const context=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844}});
 const page=await context.newPage();page.setDefaultTimeout(900000);
 page.on('pageerror',e=>report.errors.push('JS:'+String(e)));
 await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 await page.evaluate(()=>{if(document.getElementById('onboarding-overlay')&&getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 const sw=await page.evaluate(async()=>{
   const r=await navigator.serviceWorker.ready;
   return {active:!!r.active,scope:r.scope,controller:!!navigator.serviceWorker.controller,version:PUBLIC_VERSION};
 });
 verify('fresh_profile_sw_ready',sw.active&&sw.version==='142.18',sw);
 const first=await page.evaluate(async()=>await requestOfflineStatus());
 verify('fresh_profile_offline_not_prepared',first.total===204&&first.state!=='READY',
   {state:first.state,total:first.total,completed:first.completed,failed:first.failed});
 await page.evaluate(async()=>await startOfflinePreparation());
 const started=Date.now();
 await page.waitForFunction(()=>['READY','PARTIAL','ERROR','CANCELLED'].includes(offlineUiState.state),null,{timeout:1000*60*17,polling:1000});
 const ready=await page.evaluate(async()=>{
   const s=await requestOfflineStatus(60000);
   const m=await (await fetch('./offline_manifest.json',{cache:'no-store'})).json();
   return {state:s.state,completed:s.completed,total:s.total,failed:s.failed,totalBytes:s.total_bytes,
     manifestCount:m.asset_count,manifestTotalBytes:m.total_bytes,manifestBinding:m.content_binding_sha256,
     elapsedUiMessage:offlineUiState.message};
 });
 report.details.elapsed_prepare_seconds=Math.round((Date.now()-started)/1000);
 verify('verified_all_204_assets_downloaded',ready.state==='READY'&&ready.completed===204&&ready.total===204&&ready.failed.length===0,ready);
 verify('frozen_corpus_binding_preserved',ready.manifestBinding==='1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384'&&ready.manifestCount===204,ready);
 const all=await page.evaluate(async()=>{
   const m=await (await fetch('./offline_manifest.json',{cache:'no-store'})).json();
   const names=await caches.keys();const name=names.find(n=>n.includes('offline-persistent-v3-'));
   if(!name)throw Error('NO_PERSISTENT_OFFLINE_CACHE');
   const cache=await caches.open(name);
   const toHex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');
   const fails=[],check=[];
   let bytes=0,count=0;
   for(const a of m.assets){
     const response=await cache.match(new URL(a.path,location.href).href,{ignoreSearch:true});
     if(!response){fails.push({p:a.path,cause:'CACHE_MISS'});continue;}
     const raw=await response.arrayBuffer();
     const hash=toHex(await crypto.subtle.digest('SHA-256',raw));
     const ok=raw.byteLength===Number(a.bytes)&&hash===a.sha256&&
       response.headers.get('x-ldc-verified-sha256')===a.sha256;
     if(!ok)fails.push({p:a.path,cause:'BYTE_HASH_OR_MARKER_MISMATCH'});
     bytes+=raw.byteLength;count++;
     if(check.length<5)check.push({p:a.path,size:raw.byteLength,sha256:hash});
   }
   return {cache:name,verified:count,errors:fails,bytes,examples:check,
     cacheEntryCount:(await cache.keys()).length,manifestTotal:m.total_bytes};
 });
 verify('independent_browser_sha256_all_204',all.verified===204&&all.errors.length===0&&all.bytes===ready.manifestTotalBytes,all);
 await context.setOffline(true);
 await page.reload({waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:90000});
 const offline=await page.evaluate(async()=>{
   const s=await requestOfflineStatus(60000);
   const result={state:s.state,completed:s.completed,total:s.total,version:PUBLIC_VERSION,screen:document.querySelector('.screen.active')?.id||null,volumeEntries:[]};
   for(const vol of [1,18,36]){
     await ensureVolumeReaderData(vol);
     const e=corpusCache[vol]?.entries||[];
     result.volumeEntries.push({vol,n:e.length,first:e[0]?.id||null});
   }
   return result;
 });
 verify('offline_reload_and_SW_status_ready',offline.state==='READY'&&offline.completed===204&&offline.version==='142.18',offline);
 verify('offline_first_middle_last_tomes_readable',offline.volumeEntries.length===3&&offline.volumeEntries.every(x=>x.n>0),offline.volumeEntries);
 verify('no_unhandled_page_errors',report.errors.length===0,report.errors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_204_ASSET_OFFLINE_DOM_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
