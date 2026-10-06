
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
function cp(a,b){fs.rmSync(b,{recursive:true,force:true});fs.mkdirSync(path.dirname(b),{recursive:true});fs.cpSync(a,b,{recursive:true});}
const pred='24h-v119-b1-governed-r4',succ='24h-v120-b6-blind-closure';
const RID='24h-v120-b6-20261002-blind-adversarial-closure',SEQ=120000001;
const root='qa-24h-b6-rootcause-r2',dst=path.join(root,'app');
const url='http://127.0.0.1:8093/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),singleDirect:{},singleApp:{},multi:{},errors:[]};

async function setup(ctx,label){
  cp(pred,dst);
  const p=await ctx.newPage();
  const consoleAll=[]; p.on('console',m=>consoleAll.push({type:m.type(),text:m.text()})); p.on('pageerror',e=>consoleAll.push({type:'pageerror',text:String(e)}));
  await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForFunction(()=>window.__lp24Init==='done'&&APP_VERSION==='v119',null,{timeout:30000});
  await p.evaluate(()=>navigator.serviceWorker.ready);
  await p.reload({waitUntil:'domcontentloaded',timeout:30000});
  await p.waitForFunction(()=>window.__lp24Init==='done'&&navigator.serviceWorker.controller&&APP_VERSION==='v119',null,{timeout:20000});
  await p.waitForTimeout(700);
  const pre=await p.evaluate(async()=>{
    const r=await navigator.serviceWorker.getRegistration();
    return {id:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,controller:!!navigator.serviceWorker.controller,
      reg:{active:r&&r.active&&r.active.state,waiting:r&&r.waiting&&r.waiting.state,installing:r&&r.installing&&r.installing.state}};
  });
  cp(succ,dst);
  await p.waitForTimeout(100);
  return {p,pre,consoleAll,label};
}
async function remoteAndReg(p){
  return await p.evaluate(async()=>{
    const remote=normalizeRemoteRelease(await fetchJsonWithTimeout(getVersionUrl(),6500));
    const reg=await getOwnServiceWorkerRegistration();
    return {remote,regState:{active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state,installing:reg&&reg.installing&&reg.installing.state}};
  });
}
async function ensureWaiting(p){
  return await p.evaluate(async()=>{
    const remote=normalizeRemoteRelease(await fetchJsonWithTimeout(getVersionUrl(),6500));
    const reg=await getOwnServiceWorkerRegistration();
    let worker=null,err=null;
    try{worker=await findVerifiedWaitingWorker(reg,remote,45000)}catch(e){err=String(e&&e.stack||e)}
    const info=worker?await queryWorkerRelease(worker):null;
    return {remote,err,workerState:worker&&worker.state,info,
      reg:{active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state,installing:reg&&reg.installing&&reg.installing.state}};
  });
}
async function regSnapshot(p){
  return await p.evaluate(async()=>{
    const reg=await navigator.serviceWorker.getRegistration();
    let activeInfo=null,waitingInfo=null,controllerInfo=null;
    try{if(reg&&reg.active)activeInfo=await queryWorkerRelease(reg.active)}catch(e){activeInfo={error:String(e)}}
    try{if(reg&&reg.waiting)waitingInfo=await queryWorkerRelease(reg.waiting)}catch(e){waitingInfo={error:String(e)}}
    try{if(navigator.serviceWorker.controller)controllerInfo=await queryWorkerRelease(navigator.serviceWorker.controller)}catch(e){controllerInfo={error:String(e)}}
    return {url:location.href,id:typeof APP_RELEASE_ID==='undefined'?null:APP_RELEASE_ID,build:typeof BUILD_REVISION==='undefined'?null:BUILD_REVISION,
      status:document.getElementById('updateCheckStatus')?.textContent||'',
      prepared:typeof _preparedUpdate!=='undefined'&&_preparedUpdate?{mode:_preparedUpdate.mode,workerState:_preparedUpdate.worker&&_preparedUpdate.worker.state,remote:_preparedUpdate.remote&&{releaseId:_preparedUpdate.remote.releaseId,sequence:_preparedUpdate.remote.sequence}}:null,
      reg:{active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state,installing:reg&&reg.installing&&reg.installing.state},
      activeInfo,waitingInfo,controllerInfo,controller:!!navigator.serviceWorker.controller};
  });
}

(async()=>{
  const browser=await chromium.launch({headless:true});

  // A. Direct protocol, one genuine controlled v119 client.
  {
    const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    const {p,pre,consoleAll}=await setup(ctx,'singleDirect'); out.singleDirect.pre=pre;
    out.singleDirect.before=await remoteAndReg(p);
    out.singleDirect.ensure=await ensureWaiting(p);
    out.singleDirect.beforeAck=await regSnapshot(p);
    const ack=await p.evaluate(async({RID,SEQ})=>{
      const reg=await navigator.serviceWorker.getRegistration();
      if(!reg||!reg.waiting)return {type:'NO_WAITING'};
      const requestId='rootcause-direct-'+Date.now();
      try{return await postMessageWithReply(reg.waiting,{type:'ACTIVATE_UPDATE_V2',request_id:requestId,expected_release_id:RID,expected_release_sequence:SEQ},7000)}
      catch(e){return{type:'THREW',error:String(e&&e.stack||e)}}
    },{RID,SEQ});
    out.singleDirect.ack=ack;
    await p.waitForTimeout(1800);
    out.singleDirect.afterAck=await regSnapshot(p);
    out.singleDirect.console=consoleAll;
    await ctx.close();
  }

  // B. Actual page commit path, one genuine controlled v119 client.
  {
    const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    const {p,pre,consoleAll}=await setup(ctx,'singleApp'); out.singleApp.pre=pre;
    const prep=await p.evaluate(async()=>{
      const ok=await checkForUpdate(true,'rootcause-r2');
      await new Promise(r=>setTimeout(r,250));
      return {ok,snap:await (async()=>{const reg=await navigator.serviceWorker.getRegistration();return{prepared:_preparedUpdate?{mode:_preparedUpdate.mode,worker:_preparedUpdate.worker&&await queryWorkerRelease(_preparedUpdate.worker)}:null,active:reg&&reg.active&&reg.active.state,waiting:reg&&reg.waiting&&reg.waiting.state}})()};
    });
    out.singleApp.prepared=prep;
    if(!prep.snap.prepared){
      out.singleApp.ensure=await ensureWaiting(p);
      // Bind the verified waiting worker to the app's prepared-update object only if checkForUpdate was raced by another same-page check.
      await p.evaluate(async()=>{
        if(_preparedUpdate)return;
        const remote=normalizeRemoteRelease(await fetchJsonWithTimeout(getVersionUrl(),6500));
        const reg=await getOwnServiceWorkerRegistration();
        const worker=await findVerifiedWaitingWorker(reg,remote,45000);
        _preparedUpdate={remote,registration:reg,worker,mode:'waiting',preparedAt:Date.now()};
      }).catch(()=>{});
    }
    out.singleApp.beforeCommit=await regSnapshot(p);
    let navigated=null;
    p.on('framenavigated',f=>{if(f===p.mainFrame())navigated=f.url()});
    await p.evaluate(()=>{refreshAppForUpdate(); return true;});
    for(let i=0;i<50&&!navigated;i++)await p.waitForTimeout(100);
    out.singleApp.navigated=navigated;
    try{out.singleApp.afterCommit=await regSnapshot(p)}catch(e){out.singleApp.afterCommit={error:String(e)}}
    out.singleApp.console=consoleAll;
    await ctx.close();
  }

  // C. Two-client fail-closed contract. Normal auto checks are allowed to run.
  {
    cp(pred,dst);
    const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    const p1=await ctx.newPage(), p2=await ctx.newPage(); const cons=[];
    for(const [n,p] of [['p1',p1],['p2',p2]]){p.on('console',m=>cons.push({page:n,type:m.type(),text:m.text()}));p.on('pageerror',e=>cons.push({page:n,type:'pageerror',text:String(e)}))}
    await p1.goto(url,{waitUntil:'domcontentloaded'}); await p1.waitForFunction(()=>APP_VERSION==='v119'); await p1.evaluate(()=>navigator.serviceWorker.ready); await p1.reload({waitUntil:'domcontentloaded'}); await p1.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119');
    await p2.goto(url,{waitUntil:'domcontentloaded'}); await p2.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119');
    cp(succ,dst); await p1.waitForTimeout(250);
    out.multi.before=await regSnapshot(p1);
    out.multi.ensure=await ensureWaiting(p1);
    out.multi.beforeAck=await regSnapshot(p1);
    out.multi.ack=await p1.evaluate(async({RID,SEQ})=>{
      const reg=await navigator.serviceWorker.getRegistration(); if(!reg||!reg.waiting)return{type:'NO_WAITING'};
      const requestId='rootcause-multi-'+Date.now();
      try{return await postMessageWithReply(reg.waiting,{type:'ACTIVATE_UPDATE_V2',request_id:requestId,expected_release_id:RID,expected_release_sequence:SEQ},7000)}
      catch(e){return{type:'THREW',error:String(e&&e.stack||e)}}
    },{RID,SEQ});
    await p1.waitForTimeout(700);
    out.multi.afterAck=await regSnapshot(p1);
    out.multi.p2=await regSnapshot(p2);
    out.multi.console=cons;
    await ctx.close();
  }

  await browser.close();
  fs.writeFileSync('24h-b6-activation-rootcause-r2-results.json',JSON.stringify(out,null,2));
  console.log(JSON.stringify({singleDirect:{ack:out.singleDirect.ack,after:out.singleDirect.afterAck},singleApp:{prepared:out.singleApp.prepared,navigated:out.singleApp.navigated,after:out.singleApp.afterCommit},multi:{ack:out.multi.ack,after:out.multi.afterAck}},null,2));
  const sd=out.singleDirect.ack||{}, md=out.multi.ack||{};
  // Diagnostic is considered successful if it reaches and records both protocol decisions; it does not assert they are PASS.
  if(!sd.type||!md.type)process.exit(2);
})().catch(e=>{out.errors.push(String(e&&e.stack||e));try{fs.writeFileSync('24h-b6-activation-rootcause-r2-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
