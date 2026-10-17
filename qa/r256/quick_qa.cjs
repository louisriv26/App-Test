const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium,webkit}=require('playwright');
const engine=process.env.R256_BROWSER==='webkit'?webkit:chromium;
const OLD='/tmp/ldc_r256_old', NEW=process.cwd();
let currentRoot=OLD;
const report=[];
function log(name,info){const v={name, ...info};report.push(v);console.log('R256_QUICK '+JSON.stringify(v));}
const server=http.createServer(async(req,res)=>{
 try {
  const url=new URL(req.url,'http://127.0.0.1');
  let rel=decodeURIComponent(url.pathname).replace(/^\/+/,'').replace(/^App-Test\//,'')||'index.html';
  let source=path.join(currentRoot,rel);
  if(!source.startsWith(currentRoot+path.sep))throw Error('scope');
  let buf=await fs.promises.readFile(source);
  let ext=path.extname(source);
  res.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'application/javascript','.json':'application/json','.mjs':'application/javascript','.css':'text/css','.woff2':'font/woff2','.png':'image/png','.ico':'image/x-icon'}[ext]||'application/octet-stream','Cache-Control':'no-store'});
  res.end(buf);
 }catch(e){res.writeHead(404);res.end(e.message);}
});
function wait(ms){return new Promise(r=>setTimeout(r,ms))}
async function state(page){
 return page.evaluate(async()=>{
  const reg=await navigator.serviceWorker.getRegistration().catch(()=>null);
  const ctl=navigator.serviceWorker.controller||reg?.active;
  let ver=null;
  if(ctl)ver=await new Promise(resolve=>{const m=new MessageChannel();const t=setTimeout(()=>resolve('TIMEOUT'),1200);m.port1.onmessage=e=>{clearTimeout(t);resolve(e.data?.version||null)};ctl.postMessage({type:'LDC_GET_VERSION'},[m.port2])});
  const error=document.querySelector('#boot-error-code')?.textContent||'';
  const loading=document.getElementById('loading');
  return {app:typeof APP_VERSION!=='undefined'?APP_VERSION:null,stage:typeof bootStage!=='undefined'?bootStage:null,err:error,visibleLoading:loading?getComputedStyle(loading).display!=='none':null,sw:ver,controller:navigator.serviceWorker.controller?.state||null,active:reg?.active?.state||null,waiting:reg?.waiting?.state||null,installing:reg?.installing?.state||null,updateBanner:document.querySelector('.ub-text')?.innerText?.slice(0,100)||null};
 });
}
async function awaitMatch(page,fn,t=20000){
 const deadline=Date.now()+t;
 while(Date.now()<deadline){
  const s=await state(page);
  if(fn(s))return s;
  await wait(250);
 }
 return await state(page);
}
async function run(){
 const oldVersion=JSON.parse(fs.readFileSync(path.join(OLD,'version.json'),'utf8')).app_version;
 const newVersion=JSON.parse(fs.readFileSync(path.join(NEW,'version.json'),'utf8')).app_version;
 log('fixture_versions',{oldVersion,newVersion,oldPath:OLD,newPath:NEW});
 if(!newVersion.includes('142.46'))throw Error('incorrect QA candidate');
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const url='http://127.0.0.1:'+server.address().port+'/App-Test/';
 const browser=await engine.launch({headless:true});
 try {
   const errors=[];
   const fresh=await browser.newContext({serviceWorkers:'allow'});
   const page=await fresh.newPage();
   page.on('pageerror',e=>errors.push(String(e)));
   try{
    currentRoot=NEW;
    await page.goto(url,{waitUntil:'domcontentloaded',timeout:20000});
    const cold=await awaitMatch(page,s=>s.active==='activated'||!!s.err,25000);
    log('candidate_cold',{...cold});
    if(cold.err||cold.active!=='activated')throw Error('candidate fresh worker not activated');
    await page.reload({waitUntil:'domcontentloaded',timeout:20000});
    let active=await awaitMatch(page,s=>s.sw?.includes('142.46')||!!s.err,12000);
    log('candidate_cold_reload',{...active});
    if(active.err||!active.sw?.includes('142.46'))throw Error('candidate new control failure');
    log('candidate_cold_errors',{errors});
   } finally{await fresh.close();}
   const existing=await browser.newContext({serviceWorkers:'allow'}),upgrade=await existing.newPage();
   const updateErrors=[];
   upgrade.on('pageerror',e=>updateErrors.push(String(e)));
   try {
    currentRoot=OLD;
    await upgrade.goto(url,{waitUntil:'domcontentloaded',timeout:20000});
    let old=await awaitMatch(upgrade,s=>s.active==='activated'&&!s.visibleLoading,18000);
    log('old_ready',{...old});
    if(old.app!==oldVersion||old.err||old.active!=='activated')throw Error('old fixture not ready');
    currentRoot=NEW;
    const trigger=await upgrade.evaluate(async()=>{
     let r=await navigator.serviceWorker.getRegistration();
     await r.update();return 'update_requested';
    });
    log('upgrade_trigger',{trigger});
    const waiting=await awaitMatch(upgrade,s=>!!s.waiting||!!s.err,15000);
    log('new_worker_waiting',{...waiting});
    if(!waiting.waiting)throw Error('new candidate did not reach waiting');
    const outcome=await upgrade.evaluate(async()=>Promise.race([reloadForUpdate(),new Promise(r=>setTimeout(()=>r({status:'BUTTON_TIMEOUT'}),10000))]));
    log('actualiser_result',{outcome,...(await state(upgrade))});
    let ready=await awaitMatch(upgrade,s=>s.sw?.includes('142.46'),14000);
    log('update_controller',{...ready});
    if(!ready.sw?.includes('142.46')){
      const diag=await upgrade.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();const w=r?.waiting||null;const ctl=navigator.serviceWorker.controller||null;let waitingVersion=null;if(w){waitingVersion=await new Promise(resolve=>{const ch=new MessageChannel();const timer=setTimeout(()=>resolve('NO_REPLY'),1500);ch.port1.onmessage=e=>{clearTimeout(timer);resolve(e.data?.version||null)};w.postMessage({type:'LDC_GET_VERSION'},[ch.port2])});w.postMessage({type:'SKIP_WAITING'})}return {waiting:w?.state||null,waitingVersion,controller:ctl?.state||null}});
      log('actualiser_nonactivation_diagnostic',{diag});
      const retry=await awaitMatch(upgrade,s=>s.sw?.includes('142.46'),6000);
      log('activation_second_request',{...retry});
      const wk=existing.serviceWorkers();
      const ev=await Promise.all(wk.map(async(w)=>{try{return {url:w.url(),state:await Promise.race([w.evaluate(()=>({version:typeof VERSION==='undefined'?null:VERSION,waiting:self.registration.waiting?.state,active:self.registration.active?.state})),new Promise(res=>setTimeout(()=>res({timeout:true}),2500))])}}catch(e){return {url:w.url(),error:String(e)}}}));
      log('serviceworker_direct_eval',{workers:ev});
      let direct=null;const tgt=wk.length?wk[wk.length-1]:null;
      if(tgt)try{direct=await Promise.race([tgt.evaluate(async()=>{await self.skipWaiting();return {invoked:true}}),new Promise(res=>setTimeout(()=>res({timeout:true}),3000))])}catch(e){direct={error:String(e)}}
      const afterDirect=await awaitMatch(upgrade,s=>s.sw?.includes('142.46'),5000);
      log('serviceworker_direct_skipWaiting',{direct,state:afterDirect});

      if(process.env.R256_BROWSER==='webkit'){
        await upgrade.close();
        await new Promise(r=>setTimeout(r,2000));
        const reopened=await existing.newPage();
        await reopened.goto(url,{waitUntil:'domcontentloaded',timeout:20000});
        const afterClose=await awaitMatch(reopened,s=>s.sw?.includes('142.46')||!!s.err,14000);
        log('webkit_after_close_all_clients',{...afterClose});
        await reopened.close();
      }
      throw Error('Actualiser did not activate new SW on first request');
    }
    await upgrade.reload({waitUntil:'domcontentloaded',timeout:20000});
    let boot=await awaitMatch(upgrade,s=>s.app===newVersion&&!s.visibleLoading||!!s.err,18000);
    log('upgrade_final',{...boot});
    if(boot.err||boot.app!==newVersion||boot.visibleLoading)throw Error('new application not booted after upgrade');
    log('upgrade_js_errors',{errors:updateErrors});
   } finally {await existing.close();}
 } finally {await browser.close();await new Promise(r=>server.close(r));}
}
(async()=>{let passed=false;try{await run();passed=true;}catch(e){log('FAILED',{error:String(e),stack:e.stack?.slice(0,600)})}finally{fs.writeFileSync('r256-quick-results.json',JSON.stringify({passed,report},null,2))}if(!passed)process.exit(1);})();
