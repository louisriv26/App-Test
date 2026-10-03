
const {chromium}=require('playwright'); const fs=require('fs'),path=require('path');
function cp(a,b){fs.rmSync(b,{recursive:true,force:true});fs.mkdirSync(path.dirname(b),{recursive:true});fs.cpSync(a,b,{recursive:true});}
const pred='24h-v119-b1-governed-r4',succ='24h-v120-b6-blind-closure',root='qa-24h-b6-eventproof',dst=path.join(root,'app');
const url='http://127.0.0.1:8095/app/luisa_24_heures.html';
const out={};
(async()=>{
 cp(pred,dst);
 const b=await chromium.launch({headless:true}),c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'}),p=await c.newPage();
 await p.goto(url,{waitUntil:'domcontentloaded'}); await p.waitForFunction(()=>APP_VERSION==='v119'); await p.evaluate(()=>navigator.serviceWorker.ready);
 await p.reload({waitUntil:'domcontentloaded'}); await p.waitForFunction(()=>navigator.serviceWorker.controller&&APP_VERSION==='v119');
 cp(succ,dst);
 out.check=await p.evaluate(async()=>await checkForUpdate(true,'event-proof'));
 await p.waitForTimeout(200);
 out.before=await p.evaluate(async()=>({prepared:_preparedUpdate&&{mode:_preparedUpdate.mode,state:_preparedUpdate.worker.state,info:await queryWorkerRelease(_preparedUpdate.worker)}}));
 out.result=await p.evaluate(async()=>{
   const prepared=_preparedUpdate;if(!prepared||prepared.mode!=='waiting')throw new Error('not_waiting');
   const remote=prepared.remote,registration=prepared.registration,worker=prepared.worker;
   const requestId='eventproof-'+Date.now();
   const ack=await postMessageWithReply(worker,{type:'ACTIVATE_UPDATE_V2',request_id:requestId,expected_release_id:remote.releaseId,expected_release_sequence:remote.sequence},5000);
   if(!ack||ack.type!=='ACTIVATE_UPDATE_ACCEPTED_V2')return{ack,activated:false};
   const activated=await waitForWorkerState(worker,['activated'],15000);
   let workerInfo=null;if(activated)workerInfo=await queryWorkerRelease(activated);
   const controller=await waitForControllerRelease(remote,8000);
   return {ack,activated:!!activated,workerState:worker.state,workerInfo,controller:!!controller,controllerInfo:controller?await queryWorkerRelease(controller):null,reg:{active:registration.active&&registration.active.state,waiting:registration.waiting&&registration.waiting.state}};
 });
 fs.writeFileSync('24h-b6-event-wait-proof-results.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out,null,2));
 await c.close();await b.close();
 if(!out.result.activated||!out.result.controller||out.result.workerInfo.releaseId!=='24h-v120-b6-20261002-blind-adversarial-closure')process.exit(2);
})().catch(e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b6-event-wait-proof-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
