const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium, webkit} = require('playwright');
const TARGET = 'https://louisriv26.github.io/App-Test/';
const OLD = path.resolve('/tmp/ldc_r256_old');
const NEW = process.cwd();
let serveOld = true;
const results=[];
function note(tag,data){const d={tag,time:new Date().toISOString(),...data};results.push(d);console.log('R256_QA '+JSON.stringify(d));}
function delay(t){return new Promise(r=>setTimeout(r,t));}
async function snapshot(page){
 return await page.evaluate(async()=>{
  const loading=document.getElementById('loading'), error=document.getElementById('boot-error-code');
  const reg=('serviceWorker' in navigator)?await navigator.serviceWorker.getRegistration().catch(()=>null):null;
  const ctl=navigator.serviceWorker?.controller||null;
  let version=null;
  if(ctl){version=await new Promise(resolve=>{const ch=new MessageChannel();const timer=setTimeout(()=>resolve(null),700);ch.port1.onmessage=e=>{clearTimeout(timer);resolve(e.data?.version||null)};try{ctl.postMessage({type:'LDC_GET_VERSION'},[ch.port2])}catch(e){clearTimeout(timer);resolve(null)}})}
  const visible=loading&&getComputedStyle(loading).display!=='none';
  return {url:location.href,app:typeof APP_VERSION!=='undefined'?APP_VERSION:null,stage:typeof bootStage!=='undefined'?bootStage:null,visibleLoading:visible,diagnostic:error?.innerText||null,loadingText:visible?loading.innerText.slice(0,400):null,offlineState:typeof offlineUiState!=='undefined'?offlineUiState?.state:null,controllerVersion:version,controllerState:ctl?.state||null,registration:{active:reg?.active?.state||null,waiting:reg?.waiting?.state||null,installing:reg?.installing?.state||null},readyHome:document.getElementById('home-screen')?.offsetParent!==null}
 }).catch(e=>({snapshotError:String(e)}));
}
async function waitBoot(page,timeoutMs=75000){
 await page.waitForFunction(()=>{let el=document.getElementById('loading');return !!document.getElementById('boot-error-code')||(!!el&&getComputedStyle(el).display==='none');},null,{timeout:timeoutMs}).catch(()=>{});
 return snapshot(page);
}
function track(page,label){
 const errors=[];page.on('pageerror',e=>errors.push('PAGE: '+String(e).slice(0,400)));
 page.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE: '+m.text().slice(0,400))});
 page.on('requestfailed',r=>{if(/sw\.js|index\.html|supplement|manifest|version/.test(r.url()))errors.push('FETCH: '+r.url()+' '+r.failure()?.errorText)});
 return ()=>{note(label+'_errors',{errors:errors.slice(0,35)});return errors};
}
async function testLive(engine,launcher){
 const b=await launcher.launch({headless:true}),ctx=await b.newContext({serviceWorkers:'allow',viewport:{width:390,height:850}});
 try {
  const p=await ctx.newPage();const errs=track(p,engine+'_live');
  const response=await p.goto(TARGET+'?ldc_r256_cold='+Date.now(),{waitUntil:'domcontentloaded',timeout:80000});
  note(engine+'_fresh',{http:response?.status(),...(await waitBoot(p))});
  await p.waitForTimeout(9500);note(engine+'_post_install',{...(await snapshot(p))});
  const second=await ctx.newPage();const e2=track(second,engine+'_multitab');
  await second.goto(TARGET+'?ldc_r256_multitab='+Date.now(),{waitUntil:'domcontentloaded',timeout:80000});
  note(engine+'_second_tab',{...(await waitBoot(second,55000))});
  await p.reload({waitUntil:'domcontentloaded',timeout:80000});
  note(engine+'_reload_after_multitab',{...(await waitBoot(p,60000))});
  note(engine+'_status_errors',{n:errs().length+e2().length});
  await second.close();await p.close();
 }catch(e){note(engine+'_live_exception',{error:String(e).slice(0,1200)})}
 finally{await ctx.close();await b.close();}
}
const MIME={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.mjs':'application/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.woff2':'font/woff2','.woff':'font/woff','.png':'image/png','.ico':'image/x-icon'};
const server=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://127.0.0.1');
  if(url.pathname==='/qa-switch'){serveOld=url.searchParams.get('old')==='1';res.end(JSON.stringify({serveOld}));return;}
  const rel=decodeURIComponent(url.pathname).replace(/^\/+/,'')||'index.html';
  const root=serveOld?OLD:NEW;
  const p=path.resolve(root,rel);
  if(!(p===root||p.startsWith(root+path.sep))){res.writeHead(403);res.end();return}
  const contents=await fs.promises.readFile(p);
  res.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream','cache-control':'no-cache','access-control-allow-origin':'*'});
  res.end(contents);
 }catch(e){res.writeHead(404);res.end(String(e.code||e).slice(0,150))}
});
async function testUpgrade(){
 await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
 const port=server.address().port,origin='http://127.0.0.1:'+port+'/';
 const browser=await chromium.launch({headless:true});const ctx=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:850}});
 try{
  serveOld=true;
  const page=await ctx.newPage();const errs=track(page,'upgrade');
  let resp=await page.goto(origin,{waitUntil:'domcontentloaded',timeout:90000});
  note('upgrade_v14243_first',{http:resp?.status(),...(await waitBoot(page,80000))});
  await page.waitForFunction(async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.active?.state==='activated';},null,{timeout:80000}).catch(()=>{});
  note('upgrade_v14243_active',{...(await snapshot(page))});
  serveOld=false;
  const update=await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();if(!r)return 'NO_REGISTRATION';try{await r.update();return 'REG_UPDATE_OK'}catch(e){return String(e)}})
  note('upgrade_requested',{update,...(await snapshot(page))});
  await delay(10000);
  note('upgrade_after_delay',{...(await snapshot(page))});
  let button=await page.$('.ub-refresh');if(button&&await button.isVisible().catch(()=>false)){
   await button.click({timeout:20000});
   note('upgrade_clicked_actualiser',{...(await snapshot(page))});
  }else{
   const outcome=await page.evaluate(async()=>typeof reloadForUpdate==='function'?await reloadForUpdate():{error:'NO_FN'});note('upgrade_direct_actualiser',{outcome});
  }
  await delay(15000);
  note('upgrade_after_actualiser',{...(await snapshot(page))});
  resp=await page.reload({waitUntil:'domcontentloaded',timeout:90000});
  note('upgrade_after_reload',{http:resp?.status(),...(await waitBoot(page,70000))});
  errs();
 }catch(e){note('upgrade_exception',{error:String(e).slice(0,1200)})}
 finally{await ctx.close();await browser.close();await new Promise(resolve=>server.close(resolve))}
}
(async()=>{
 try{
  await testLive('chromium',chromium);
  await testLive('webkit',webkit);
  if(fs.existsSync(OLD+'/sw.js'))await testUpgrade();else note('upgrade_skipped',{reason:'historical checkout unavailable'});
 }catch(e){note('harness_exception',{error:String(e)})}
 fs.writeFileSync('r256-sw-diagnostics.json',JSON.stringify({scope:'QA isolated temporary browser context; no modification of live App-Test; local upgrade 142.43->142.45',results},null,2));
 note('summary',{cases:results.length,blocked:results.filter(x=>x.diagnostic||/exception/.test(x.tag)).length});
})().then(()=>process.exit(0),e=>{console.error(e);process.exit(1)});
