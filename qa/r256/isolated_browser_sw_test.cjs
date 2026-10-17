const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {chromium,webkit}=require('playwright');
const OLD='/tmp/ldc_r256_old',NEW=process.cwd();let phase='old';
const report=[];const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function emit(name,data={}){const v={name,at:new Date().toISOString(),...data};report.push(v);console.log('R256_ISOLATED '+JSON.stringify(v))}
const html='<!doctype html><meta charset="utf-8"><title>Minimal SW</title><script>async function register(){return navigator.serviceWorker.register("./sw.js",{updateViaCache:"none"})}register();</script>';
function miniSW(v){return 'const V='+JSON.stringify(v)+';self.addEventListener("install",e=>{e.waitUntil(Promise.resolve())});self.addEventListener("activate",e=>{e.waitUntil(self.clients.claim())});self.addEventListener("message",e=>{if(e.data?.type==="PING"){e.ports[0]?.postMessage(V)}if(e.data?.type==="SKIP_WAITING"){e.waitUntil(self.skipWaiting())}});'}
const server=http.createServer((req,res)=>{
 let url=new URL(req.url,'http://localhost');
 let p=decodeURIComponent(url.pathname).replace(/^\/+/,'');
 if(p.startsWith('mini/')){
   const v=phase==='old'?'MINI_A':'MINI_B';
   const script=p==='mini/sw.js';
   res.writeHead(200,{'content-type':script?'text/javascript':'text/html','cache-control':'no-store'});
   res.end(script?miniSW(v):html);return;
 }
 if(p.startsWith('App-Test/')){
    const file=p.slice('App-Test/'.length)||'index.html',root=phase==='old'?OLD:NEW;
    const loc=path.resolve(root,file);
    if(!loc.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
    fs.readFile(loc,(err,b)=>{
      if(err){res.writeHead(404);res.end();return}
      res.writeHead(200,{'content-type':{'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.css':'text/css','.woff2':'font/woff2','.png':'image/png'}[path.extname(loc)]||'application/octet-stream','cache-control':'no-store'});res.end(b);
    });return;
 }
 res.writeHead(404);res.end()
});
async function info(pg,mini=false){
 return await pg.evaluate(async(isMini)=>{
 const reg=await navigator.serviceWorker.getRegistration();
 const w=navigator.serviceWorker.controller||reg?.active;
 let v=null;if(w)v=await new Promise(r=>{const ch=new MessageChannel(),t=setTimeout(()=>r('TIMEOUT'),1000);ch.port1.onmessage=e=>{clearTimeout(t);r(isMini?e.data:e.data?.version)};w.postMessage({type:isMini?'PING':'LDC_GET_VERSION'},[ch.port2])});
 return {reg:!!reg,controller:!!navigator.serviceWorker.controller,active:reg?.active?.state,waiting:reg?.waiting?.state,installing:reg?.installing?.state,v,app:isMini?'mini':typeof APP_VERSION!=='undefined'?APP_VERSION:null,stage:isMini?'mini':typeof bootStage!=='undefined'?bootStage:null};
 },mini)
}
async function poll(pg,fn,ms=7000,mini=false){let end=Date.now()+ms,s;do{s=await info(pg,mini);if(fn(s))return s;await sleep(220)}while(Date.now()<end);return s}
async function test(engine,kind,mode){
 phase='old';let browser=await engine.launch({headless:true}),ctx=await browser.newContext({serviceWorkers:'allow'}),page=await ctx.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(String(e).slice(0,150)));
 const which=engine===chromium?'Chromium':'WebKit';
 const origin='http://127.0.0.1:'+server.address().port+'/'+(kind==='mini'?'mini':'App-Test')+'/';
 try{
  await page.goto(origin,{waitUntil:'domcontentloaded',timeout:30000});
  let old=await poll(page,s=>s.active==='activated'&&(kind==='mini'||s.stage==='POST_INIT'),20000,kind==='mini');
  emit('old',{engine:which,kind,mode,old});
  phase='new';
  await page.evaluate(async()=>{let r=await navigator.serviceWorker.getRegistration();await r.update()});
  let waiting=await poll(page,s=>s.waiting==='installed',15000,kind==='mini');
  emit('waiting',{engine:which,kind,mode,waiting});
  if(waiting.waiting!=='installed')return;
  if(mode==='postMessage'){
   await page.evaluate(async()=>{let reg=await navigator.serviceWorker.getRegistration();reg.waiting.postMessage({type:'SKIP_WAITING'})});
   const after=await poll(page,s=>s.v?.includes(kind==='mini'?'MINI_B':'142.46'),8000,kind==='mini');
   emit('post-message-result',{engine:which,kind,mode,after});
  }
  if(mode==='closeTab'){
    await page.close();await sleep(2200);page=await ctx.newPage();await page.goto(origin,{waitUntil:'domcontentloaded',timeout:30000});
    const x=await poll(page,s=>s.v?.includes(kind==='mini'?'MINI_B':'142.46'),20000,kind==='mini');
    emit('after-close-reopen',{engine:which,kind,mode,x});
  }
  emit('errors',{engine:which,kind,mode,errors});
 }catch(e){emit('test-exception',{engine:which,kind,mode,error:String(e).slice(0,400)})}
 finally{await ctx.close();await browser.close()}
}
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{
   for(let engine of [chromium,webkit]){
     for(let kind of ['mini','app']){
       for(let mode of ['postMessage','closeTab']){
         const runs=(kind==='app'&&mode==='postMessage')?6:2;
         for(let attempt=1;attempt<=runs;attempt++)await test(engine,kind,mode);
       }
     }
   }
   const groups={};for(const r of report){
      if(r.name!=='post-message-result'&&r.name!=='after-close-reopen')continue;
      const key=r.engine+'|'+r.kind+'|'+r.mode;
      if(!groups[key])groups[key]={runs:0,activated:0};
      groups[key].runs++;
      const state=r.after||r.x;
      if(state?.v?.includes(r.kind==='mini'?'MINI_B':'142.46'))groups[key].activated++;
   }
   emit('empirical_activation_rates',{groups});
 }finally{
  await new Promise(r=>server.close(r));
  fs.writeFileSync('r256-isolated-webkit-results.json',JSON.stringify(report,null,2));
 }
})().catch(e=>{console.error(e);process.exit(1)});
