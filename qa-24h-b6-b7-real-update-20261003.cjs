const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
const pred='24h-v120-b6-darkmode',succ='24h-v120-b7-darkmode',root='qa-24h-b6-b7-real',dst=path.join(root,'app');
function cp(a,b){fs.rmSync(b,{recursive:true,force:true});fs.mkdirSync(path.dirname(b),{recursive:true});fs.cpSync(a,b,{recursive:true});}
(async()=>{
 cp(pred,dst);const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'});let p=await c.newPage();const logs=[];p.on('console',m=>logs.push({t:m.type(),x:m.text()}));p.on('pageerror',e=>logs.push({t:'pageerror',x:String(e)}));
 const u='http://127.0.0.1:8094/app/luisa_24_heures.html';
 await p.goto(u,{waitUntil:'domcontentloaded',timeout:120000});await p.waitForFunction(()=>window.__lp24Init==='done'&&APP_RELEASE_SEQUENCE===120000006,null,{timeout:30000});await p.evaluate(()=>navigator.serviceWorker.ready);
 await p.reload({waitUntil:'domcontentloaded',timeout:30000});await p.waitForFunction(()=>window.__lp24Init==='done'&&navigator.serviceWorker.controller&&APP_RELEASE_SEQUENCE===120000006,null,{timeout:30000});
 await p.evaluate(()=>localStorage.setItem('APP_GOV_SENTINEL','b6-b7-real'));
 const pre=await p.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();let ci=null;try{ci=await queryWorkerRelease(navigator.serviceWorker.controller)}catch(e){}return{id:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,controller:ci,active:r?.active?.state,waiting:r?.waiting?.state}});
 cp(succ,dst);await p.waitForTimeout(150);
 const prepared=await p.evaluate(async()=>{const ok=await checkForUpdate(true,'qa-b6-b7-real');await new Promise(r=>setTimeout(r,300));return{ok,prepared:!!_preparedUpdate,mode:_preparedUpdate?.mode||null,remote:_preparedUpdate?.remote?{id:_preparedUpdate.remote.releaseId,seq:_preparedUpdate.remote.sequence}:null,worker:_preparedUpdate?.worker?await queryWorkerRelease(_preparedUpdate.worker):null,status:document.getElementById('updateCheckStatus')?.textContent||''}});
 if(!prepared.prepared||prepared.remote?.seq!==120000007)throw new Error('B7 not prepared '+JSON.stringify(prepared));
 let navigations=[];p.on('framenavigated',f=>{if(f===p.mainFrame())navigations.push(f.url())});
 await p.evaluate(()=>refreshAppForUpdate());
 for(let i=0;i<100;i++){try{const q=await p.evaluate(()=>({done:window.__lp24Init==='done',seq:typeof APP_RELEASE_SEQUENCE==='number'?APP_RELEASE_SEQUENCE:null,controlled:!!navigator.serviceWorker.controller}));if(q.done&&q.seq===120000007&&q.controlled)break}catch(e){}await p.waitForTimeout(100)}
 const post=await p.evaluate(async()=>{let ci=null;try{ci=await queryWorkerRelease(navigator.serviceWorker.controller)}catch(e){}return{id:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,s:localStorage.getItem('APP_GOV_SENTINEL'),controller:ci,title:document.title,caches:await caches.keys()}});
 if(post.seq!==120000007||post.s!=='b6-b7-real'||post.controller?.release_sequence!==120000007)throw new Error('post-commit mismatch '+JSON.stringify(post));
 await c.setOffline(true);await p.reload({waitUntil:'domcontentloaded',timeout:30000});await p.waitForFunction(()=>window.__lp24Init==='done',null,{timeout:20000});const off=await p.evaluate(async()=>{let ci=null;try{ci=await queryWorkerRelease(navigator.serviceWorker.controller)}catch(e){}return{id:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,s:localStorage.getItem('APP_GOV_SENTINEL'),controller:ci,title:document.title,body:(document.body.innerText||'').slice(0,160)}});
 if(off.seq!==120000007||off.s!=='b6-b7-real'||off.controller?.release_sequence!==120000007||!off.title||!off.body)throw new Error('offline mismatch '+JSON.stringify(off));
 if(logs.some(x=>x.t==='pageerror'))throw new Error('page errors '+JSON.stringify(logs));
 console.log(JSON.stringify({pre,prepared,navigations,post,off,logs},null,2));console.log('B6_B7_REAL_UPDATE_OFFLINE_PASS');await c.close();await b.close();
})().catch(e=>{console.error(e);process.exit(2)});