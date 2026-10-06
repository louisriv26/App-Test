
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
const pred='24h-v119-b1-governed-r4',succ='24h-v120-b6-blind-closure',dst=path.join('qa-24h-b6-multiclient','app');
const url='http://127.0.0.1:8087/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),steps:{}};
(async()=>{
 copy(pred,dst);
 const browser=await chromium.launch({headless:true});
 const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
 let p1=await ctx.newPage();
 await p1.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
 await p1.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v119');
 await p1.evaluate(()=>navigator.serviceWorker.ready);
 await p1.reload({waitUntil:'domcontentloaded'});
 await p1.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119');
 let p2=await ctx.newPage();
 await p2.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
 await p2.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119');
 out.steps.pre=await p1.evaluate(async()=>({id:APP_RELEASE_ID,controller:!!navigator.serviceWorker.controller,clients:await (async()=>{const r=await navigator.serviceWorker.ready;return {active:!!r.active}})()}));

 copy(succ,dst);
 const prep=await p1.evaluate(async()=>{
   const ok=await checkForUpdate(true,'multi-client');
   await new Promise(r=>setTimeout(r,200));
   return {ok,mode:_preparedUpdate&&_preparedUpdate.mode,waiting:_preparedUpdate&&_preparedUpdate.registration.waiting&&_preparedUpdate.registration.waiting.state,worker:_preparedUpdate&&_preparedUpdate.worker?await queryWorkerRelease(_preparedUpdate.worker):null};
 });
 out.steps.prepared=prep;
 if(!prep.mode||prep.mode!=='waiting'||prep.waiting!=='installed')throw new Error('b6_not_waiting_with_two_clients');

 const rejected=await p1.evaluate(async()=>{
   const result=await refreshAppForUpdate();
   await new Promise(r=>setTimeout(r,150));
   const reg=await navigator.serviceWorker.getRegistration();
   return {result,id:APP_RELEASE_ID,build:BUILD_REVISION,status:document.getElementById('updateCheckStatus')?.textContent||'',waiting:reg&&reg.waiting&&reg.waiting.state,controller:!!navigator.serviceWorker.controller};
 });
 out.steps.rejectedWithPeer=rejected;
 if(rejected.result!==false||rejected.id!=='24h-v119-b1-20261001-adversarial-ux-correction'||!rejected.waiting)throw new Error('multi_client_fail_closed_contract_broken');

 await p2.close();
 const nav=p1.waitForURL(u=>u.href.includes('lp_update_tx=')&&u.pathname.endsWith('/luisa_24_heures.html'),{timeout:30000,waitUntil:'domcontentloaded'});
 await p1.locator('.update-refresh-btn').click();
 await nav;
 await p1.waitForFunction(()=>APP_VERSION==='v120'&&BUILD_REVISION==='B6'&&navigator.serviceWorker.controller,null,{timeout:30000});
 const post=await p1.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return{id:APP_RELEASE_ID,build:BUILD_REVISION,worker:await queryWorkerRelease(r.active),caches:await caches.keys()}});
 out.steps.afterPeerClosed=post;
 if(post.id!=='24h-v120-b6-20261002-blind-adversarial-closure'||post.build!=='B6'||post.worker.releaseId!==post.id)throw new Error('update_after_peer_close_failed');
 fs.writeFileSync('24h-b6-multiclient-failclosed-results.json',JSON.stringify(out,null,2));
 console.log('24H_B6_MULTICLIENT_FAILCLOSED_PASS');
 await ctx.close();await browser.close();
})().catch(e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b6-multiclient-failclosed-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
