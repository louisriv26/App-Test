
const {chromium}=require('playwright'); const fs=require('fs'),path=require('path');
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
const pred='24h-v119-b1-governed-r4',succ='24h-v120-b6-blind-closure',root='qa-24h-b6-activation-diag',dst=path.join(root,'app');
const url='http://127.0.0.1:8088/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),direct:{},app:{}};
async function setup(ctx){
 copy(pred,dst);
 const p=await ctx.newPage();
 await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
 await p.waitForFunction(()=>window.__lp24Init==='done'&&APP_VERSION==='v119',null,{timeout:30000});
 await p.evaluate(()=>navigator.serviceWorker.ready);
 await p.reload({waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>window.__lp24Init==='done'&&navigator.serviceWorker.controller&&APP_VERSION==='v119',null,{timeout:20000});
 copy(succ,dst);
 const prep=await p.evaluate(async()=>{await checkForUpdate(true,'diag');await new Promise(r=>setTimeout(r,200));const u=_preparedUpdate;return{mode:u&&u.mode,worker:u&&u.worker?await queryWorkerRelease(u.worker):null,waiting:u&&u.registration.waiting&&u.registration.waiting.state,active:u&&u.registration.active&&u.registration.active.state}});
 return {p,prep};
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 // Scenario A: direct protocol request to waiting worker.
 {
   const ctx=await browser.newContext({viewport:{width:390,height:844}});
   const {p,prep}=await setup(ctx); out.direct.prep=prep;
   if(prep.mode!=='waiting'||prep.waiting!=='installed')throw new Error('direct_not_waiting');
   const direct=await p.evaluate(async()=>{
     const u=_preparedUpdate; const requestId='diag-direct-'+Date.now();
     const ack=await postMessageWithReply(u.worker,{type:'ACTIVATE_UPDATE_V2',request_id:requestId,expected_release_id:u.remote.releaseId,expected_release_sequence:u.remote.sequence},5000);
     await new Promise(r=>setTimeout(r,1000));
     const reg=await navigator.serviceWorker.getRegistration();
     return {ack,reg:{installing:reg.installing&&reg.installing.state,waiting:reg.waiting&&reg.waiting.state,active:reg.active&&reg.active.state},controller:!!navigator.serviceWorker.controller,controllerInfo:navigator.serviceWorker.controller?await queryWorkerRelease(navigator.serviceWorker.controller):null};
   });
   out.direct.result=direct;
   await ctx.close();
 }
 // Scenario B: actual page updater, capturing return/console if it refuses.
 {
   const ctx=await browser.newContext({viewport:{width:390,height:844}});
   const {p,prep}=await setup(ctx); out.app.prep=prep; const consoleAll=[];
   p.on('console',m=>consoleAll.push({type:m.type(),text:m.text()}));
   const nav=p.waitForURL(u=>u.href.includes('lp_update_tx='),{timeout:10000,waitUntil:'domcontentloaded'}).then(()=>({kind:'nav',url:p.url()})).catch(e=>({kind:'nav-timeout',error:String(e)}));
   const ev=p.evaluate(async()=>{
     try{
       const result=await refreshAppForUpdate();
       const reg=await navigator.serviceWorker.getRegistration();
       return {kind:'return',result,status:document.getElementById('updateCheckStatus')?.textContent||'',reg:{installing:reg&&reg.installing&&reg.installing.state,waiting:reg&&reg.waiting&&reg.waiting.state,active:reg&&reg.active&&reg.active.state},id:APP_RELEASE_ID,build:BUILD_REVISION};
     }catch(e){return{kind:'page-catch',error:String(e)}}
   }).then(x=>x).catch(e=>({kind:'eval-error',error:String(e)}));
   const first=await Promise.race([nav,ev]);
   out.app.first=first;
   if(first.kind!=='nav') {
     out.app.eval=await ev; out.app.nav=await nav;
     try{out.app.after=await p.evaluate(async()=>{const reg=await navigator.serviceWorker.getRegistration();return{url:location.href,id:APP_RELEASE_ID,build:BUILD_REVISION,status:document.getElementById('updateCheckStatus')?.textContent||'',prepared:_preparedUpdate?{mode:_preparedUpdate.mode,worker:_preparedUpdate.worker&&await queryWorkerRelease(_preparedUpdate.worker)}:null,reg:{waiting:reg&&reg.waiting&&reg.waiting.state,active:reg&&reg.active&&reg.active.state}}})}catch(e){out.app.after={error:String(e)}}
   } else {
     await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120',null,{timeout:10000});
     out.app.after=await p.evaluate(()=>({url:location.href,id:APP_RELEASE_ID,build:BUILD_REVISION}));
   }
   out.app.console=consoleAll;
   await ctx.close();
 }
 await browser.close();
 fs.writeFileSync('24h-b6-activation-diagnostic-results.json',JSON.stringify(out,null,2));
 console.log('24H_B6_ACTIVATION_DIAGNOSTIC_COMPLETE');
})().catch(e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b6-activation-diagnostic-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
