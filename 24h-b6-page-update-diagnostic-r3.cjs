
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
function cp(a,b){fs.rmSync(b,{recursive:true,force:true});fs.mkdirSync(path.dirname(b),{recursive:true});fs.cpSync(a,b,{recursive:true});}
const pred='24h-v119-b1-governed-r4',succ='24h-v120-b6-blind-closure';
const root='qa-24h-b6-page-r3',dst=path.join(root,'app'),url='http://127.0.0.1:8094/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),steps:{},console:[]};
async function snap(p){
 return await p.evaluate(async()=>{
  const reg=await navigator.serviceWorker.getRegistration();
  const q=async w=>{try{return w?await queryWorkerRelease(w):null}catch(e){return{error:String(e)}}};
  return {url:location.href,id:APP_RELEASE_ID,build:BUILD_REVISION,seq:APP_RELEASE_SEQUENCE,status:document.getElementById('updateCheckStatus')?.textContent||'',
   prepared:_preparedUpdate?{mode:_preparedUpdate.mode,workerState:_preparedUpdate.worker&&_preparedUpdate.worker.state,remote:_preparedUpdate.remote&&{id:_preparedUpdate.remote.releaseId,seq:_preparedUpdate.remote.sequence}}:null,
   reg:{active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state,installing:reg&&reg.installing&&reg.installing.state},
   activeInfo:await q(reg&&reg.active),waitingInfo:await q(reg&&reg.waiting),controllerInfo:await q(navigator.serviceWorker.controller),
   personalActivity:typeof _personalCommitActivity==='number'?_personalCommitActivity:null,
   passivePending:typeof _passivePositionPending==='object'&&_passivePositionPending?Object.keys(_passivePositionPending).length:null,
   passiveRunning:typeof _passivePositionCommitRunning!=='undefined'?_passivePositionCommitRunning:null,
   unsavedDraft:hasUnsavedNoteDraft()};
 });
}
(async()=>{
 cp(pred,dst);
 const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
 const p=await c.newPage();p.on('console',m=>out.console.push({type:m.type(),text:m.text()}));p.on('pageerror',e=>out.console.push({type:'pageerror',text:String(e)}));
 await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
 await p.waitForFunction(()=>window.__lp24Init==='done'&&APP_VERSION==='v119',null,{timeout:30000});
 await p.evaluate(()=>navigator.serviceWorker.ready);await p.reload({waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119',null,{timeout:20000});
 await p.waitForTimeout(700);
 out.steps.pre=await snap(p);
 cp(succ,dst);await p.waitForTimeout(100);
 out.steps.check=await p.evaluate(async()=>({ok:await checkForUpdate(true,'page-r3'),status:document.getElementById('updateCheckStatus')?.textContent||''}));
 await p.waitForTimeout(250);
 out.steps.prepared=await snap(p);
 if(!out.steps.prepared.prepared||out.steps.prepared.prepared.mode!=='waiting')throw new Error('not_prepared_waiting');
 const navP=p.waitForURL(u=>u.href.includes('lp_update_tx=')&&u.pathname.endsWith('/luisa_24_heures.html'),{timeout:20000,waitUntil:'domcontentloaded'})
   .then(()=>({kind:'nav',url:p.url()})).catch(e=>({kind:'nav-timeout',error:String(e)}));
 const evalP=p.evaluate(async()=>{
   try{
     const t0=Date.now();
     const result=await refreshAppForUpdate();
     const reg=await navigator.serviceWorker.getRegistration();
     return {kind:'return',elapsed:Date.now()-t0,result,status:document.getElementById('updateCheckStatus')?.textContent||'',
       reg:{active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state},id:APP_RELEASE_ID,build:BUILD_REVISION};
   }catch(e){return{kind:'page-catch',error:String(e&&e.stack||e)}}
 }).catch(e=>({kind:'eval-error',error:String(e)}));
 out.steps.first=await Promise.race([navP,evalP]);
 if(out.steps.first.kind==='nav'){out.steps.nav=out.steps.first;out.steps.eval=await Promise.race([evalP,new Promise(r=>setTimeout(()=>r({kind:'eval-pending-after-nav'}),2500))]);}
 else {out.steps.eval=out.steps.first;out.steps.nav=await navP;}
 try{await p.waitForTimeout(500);out.steps.final=await snap(p)}catch(e){out.steps.final={error:String(e)}}
 fs.writeFileSync('24h-b6-page-update-diagnostic-r3-results.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out,null,2));
 await c.close();await b.close();
 // Diagnostic passes as execution if we captured either a successful nav or a returned page-side result.
 if(!out.steps.first||!out.steps.first.kind)process.exit(2);
})().catch(e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b6-page-update-diagnostic-r3-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
