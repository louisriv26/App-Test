'use strict';
// R256 isolated acceptance. It reads the candidate built into workspace by build_r256.py.
// Every browser context is disposable, and no real user data or published deployment is touched.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const { chromium, webkit }=require('playwright');
const NEW=process.cwd(),OLD='/tmp/ldc_r256_old',CHECK='v2.19.142.46-R1B-UNIFIED';
let previous=false;
const results=[],started=Date.now();
const result=(name,status,detail)=>{let o={name,status,detail};results.push(o);console.log('R256_ACCEPT '+JSON.stringify(o));};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const server=http.createServer((req,res)=>{
 try{let u=new URL(req.url,'http://127.0.0.1'),p=decodeURIComponent(u.pathname).replace(/^\/App-Test\/?/,'').replace(/^\//,'')||'index.html',base=previous?OLD:NEW,full=path.resolve(base,p);if(!full.startsWith(base+'/'))throw Error('scope');let b=fs.readFileSync(full),ext=path.extname(full);
 let mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.css':'text/css','.woff2':'font/woff2','.woff':'font/woff','.png':'image/png','.ico':'image/x-icon'}[ext]||'application/octet-stream';
 res.writeHead(200,{'content-type':mime,'cache-control':'no-store'});res.end(b)
 }catch(e){res.writeHead(404);res.end(String(e.message))}
});
const remoteVersion=async page=>page.evaluate(async()=>{
 let reg=await navigator.serviceWorker.getRegistration();
 let w=navigator.serviceWorker.controller||reg?.active||reg?.waiting||null;
 let version=await new Promise(resolve=>{
  if(!w)return resolve(null);let ch=new MessageChannel(),done=false;
  let end=x=>{if(done)return;done=true;clearTimeout(timer);resolve(x);ch.port1.close()};
  let timer=setTimeout(()=>end(null),2000);
  ch.port1.onmessage=e=>end(e.data?.type==='LDC_SW_VERSION'?e.data.version:null);
  try{w.postMessage({type:'LDC_GET_VERSION'},[ch.port2])}catch(e){end(null)}
 });
 return {app:typeof APP_VERSION==='undefined'?null:APP_VERSION,stage:typeof bootStage==='undefined'?null:bootStage,bootError:document.querySelector('#boot-error-code')?.textContent||null,loading:document.querySelector('#loading')?.style.display,version,sw:{active:reg?.active?.state||null,waiting:reg?.waiting?.state||null,installing:reg?.installing?.state||null},controller:!!navigator.serviceWorker.controller,offline:typeof offlineUiState==='undefined'?null:offlineUiState.state}
});
async function waitCondition(page,fn,ms=18000){return page.waitForFunction(fn,null,{timeout:ms,polling:200}).then(()=>true,()=>false)}
async function scopeCase(browserType,site,old=false){
 const browser=await browserType.launch(),context=await browser.newContext({serviceWorkers:'allow'});
 const capture=[],page=await context.newPage(),tag=browserType.name()+(old?'_upgrade':'_fresh');
 try{
  context.on('serviceworker',w=>w.on('console',m=>{if(m.type()==='error')capture.push(m.text())}));
  page.on('pageerror',e=>capture.push(String(e)));
  let response=await page.goto(site+'?r256='+tag,{waitUntil:'domcontentloaded',timeout:18000});
  const booted=await waitCondition(page,()=>{let e=document.getElementById('loading');return !!e&&(e.style.display==='none'||!!document.getElementById('boot-error-code'))},12000);
  const active=await waitCondition(page,async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.active?.state==='activated'},17000);
  let state=await remoteVersion(page);
  result(tag+'_boot',booted&&!state.bootError?'PASS':'FAIL',{http:response?.status(),booted,...state});
  result(tag+'_sw',active&&state.version?.includes('142.' )?'PASS':'FAIL',{...state,errors:capture.slice(-5)});
  return {browser,context,page,capture,state};
 }catch(e){result(tag+'_fatal','FAIL',{error:String(e),errors:capture});await context.close();await browser.close();return null}
}
async function testFresh(engine,site){
 previous=false;
 let x=await scopeCase(engine,site);if(!x)return;
 try{
  let st=x.state;
  result(engine.name()+'_r256_version',st.app===CHECK&&st.version==='ldc-v2.19.142.46-r1b-unified'?'PASS':'FAIL',st);
  let offline=await x.page.evaluate(async()=>{
   let worker=navigator.serviceWorker.controller||(await navigator.serviceWorker.getRegistration())?.active;if(!worker)return 'NO_WORKER';
   return new Promise(resolve=>{let id='r256_'+Date.now(),done=false;
   let handler=e=>{if(e.data?.type==='LDC_OFFLINE_STATUS'&&e.data.request_id===id)finish(e.data.state)};
   let finish=v=>{if(done)return;done=true;clearTimeout(timer);navigator.serviceWorker.removeEventListener('message',handler);resolve(v)};
   let timer=setTimeout(()=>finish('NO_RESPONSE'),12000);
   navigator.serviceWorker.addEventListener('message',handler);worker.postMessage({type:'OFFLINE_STATUS',request_id:id})
   })
  });
  result(engine.name()+'_offline_status',['NOT_PREPARED','PARTIAL','READY'].includes(offline)?'PASS':'FAIL',{offline});
 }finally{await x.context.close();await x.browser.close()}
}
async function testUpgrade(site){
 previous=true;
 let x=await scopeCase(chromium,site,true);if(!x)return;
 let {page,context,browser}=x;
 try{
  await page.evaluate(()=>localStorage.setItem('r256_synthetic_sentinel','preserved-20261017'));
  // Preserve this page's old controller, switch only the server's files, then request the update.
  previous=false;
  let update=await page.evaluate(async()=>{
   const reg=await navigator.serviceWorker.getRegistration();
   if(!reg)return 'NO_REGISTRATION';
   try{await reg.update();return 'UPDATE_REQUESTED'}catch(e){return String(e)}
  });
  const waiting=await waitCondition(page,async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.waiting?.state==='installed'},20000);
  result('upgrade_waiting',waiting?'PASS':'FAIL',{update,old:await remoteVersion(page)});
  if(waiting){
   const before=await page.evaluate(async()=>{
    let r=await navigator.serviceWorker.getRegistration();
    let old=await new Promise(resolve=>{let w=navigator.serviceWorker.controller,ch=new MessageChannel(),timer=setTimeout(()=>resolve(null),1000);ch.port1.onmessage=e=>{clearTimeout(timer);resolve(e.data?.version)};w.postMessage({type:'LDC_GET_VERSION'},[ch.port2])});
    r.waiting.postMessage({type:'SKIP_WAITING'});return {old}
   });
   const adopted=await waitCondition(page,async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.active?.state==='activated'&&r.active===navigator.serviceWorker.controller},20000);
   result('upgrade_controller_change',adopted?'PASS':'FAIL',{before,now:await remoteVersion(page)});
  }
  // A fresh navigation in this same origin tests integration with old stored data.
  let page2=await context.newPage();
  try{
   await page2.goto(site+'?r256=upgrade_next',{waitUntil:'commit',timeout:18000});
   let done=await waitCondition(page2,()=>{let e=document.querySelector('#loading');return !!e&&(e.style.display==='none'||!!document.querySelector('#boot-error-code'))},18000);
   let st=await remoteVersion(page2);
   let stored=await page2.evaluate(()=>localStorage.getItem('r256_synthetic_sentinel'));
   result('upgrade_new_tab',done&&!st.bootError&&st.app===CHECK&&stored==='preserved-20261017'?'PASS':'FAIL',{done,stored,...st});
  }catch(e){result('upgrade_new_tab','FAIL',{error:String(e)})}finally{await page2.close().catch(()=>{})}
 }catch(e){result('upgrade_fatal','FAIL',{error:String(e)})}
 finally{await context.close().catch(()=>{});await browser.close().catch(()=>{})}
}
(async()=>{
 const deadline=setTimeout(()=>{result('harness_timeout','FAIL',{elapsed:Date.now()-started});finish(2)},140000);
 let finishing=false;function finish(code=0){if(finishing)return;finishing=true;clearTimeout(deadline);fs.writeFileSync('r256-acceptance.json',JSON.stringify({source_version:CHECK,tests:results},null,2));server.close();process.exit(code)}
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));let site='http://127.0.0.1:'+server.address().port+'/App-Test/';
  await testFresh(chromium,site);
  await testFresh(webkit,site);
  await testUpgrade(site);
  let fails=results.filter(x=>x.status==='FAIL');result('summary',fails.length?'FAIL':'PASS',{passes:results.filter(x=>x.status==='PASS').length,failures:fails.map(x=>x.name)});
  finish(fails.length?1:0)
 }catch(e){result('harness_unhandled','FAIL',{error:String(e)});finish(2)}
})();
