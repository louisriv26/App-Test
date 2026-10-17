const {chromium,webkit}=require('playwright'),http=require('node:http');
let run=0,variant='waitUntil',phase='old';const results=[];
const server=http.createServer((req,res)=>{
 const p=new URL(req.url,'http://localhost').pathname;
 res.setHeader('Cache-Control','no-store');
 if(p.endsWith('/sw.js')){
   res.setHeader('Content-Type','text/javascript');
   let ver=phase==='old'?'A':'B',statement={waitUntil:'e.waitUntil(self.skipWaiting());',unawaited:'self.skipWaiting();',promise:'Promise.resolve().then(()=>self.skipWaiting());',sync:'self.skipWaiting();e.waitUntil(Promise.resolve());'}[variant];
   res.end('const V='+JSON.stringify(ver)+';self.addEventListener("install",e=>{e.waitUntil(Promise.resolve())});self.addEventListener("activate",e=>{e.waitUntil(self.clients.claim())});self.addEventListener("message",e=>{if(e.data?.t==="PING")e.ports[0]?.postMessage(V);if(e.data?.t==="SKIP"){e.ports[0]?.postMessage("RECEIVED");'+statement+'}})');return;
 }
 res.setHeader('Content-Type','text/html');res.end('<script>navigator.serviceWorker.register("./sw.js",{updateViaCache:"none"})</script>');
});
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function test(browserName,browser){
 phase='old';
 let context=await browser.newContext({serviceWorkers:'allow'}),page=await context.newPage(),base='http://127.0.0.1:'+server.address().port+'/mini/';
 let result={browser:browserName,variant,run:run};
 try{
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.active?.state==='activated'},null,{timeout:10000});
  phase='new';
  await page.evaluate(async()=>{let r=await navigator.serviceWorker.getRegistration();await r.update()});
  await page.waitForFunction(async()=>{let r=await navigator.serviceWorker.getRegistration();return r?.waiting?.state==='installed'},null,{timeout:10000});
  result.ack=await page.evaluate(async()=>{
   let r=await navigator.serviceWorker.getRegistration(),ch=new MessageChannel();
   return await new Promise(resolve=>{let t=setTimeout(()=>resolve('TIMEOUT'),900);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.waiting.postMessage({t:'SKIP'},[ch.port2]);})
  });
  try{
   await page.waitForFunction(async()=>{let r=await navigator.serviceWorker.getRegistration();if(!r?.active)return false;let ch=new MessageChannel();return await new Promise(resolve=>{let t=setTimeout(()=>resolve(false),400);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data==='B')};r.active.postMessage({t:'PING'},[ch.port2]);})},null,{timeout:3500});
   result.activated=true;
  }catch(e){result.activated=false}
  if(!result.activated){
    await page.close();await wait(500);page=await context.newPage();await page.goto(base,{waitUntil:'domcontentloaded'});
    const state=await page.evaluate(async()=>{let r=await navigator.serviceWorker.getRegistration(),ch=new MessageChannel();if(!r.active)return null;return await new Promise(resolve=>{let t=setTimeout(()=>resolve(null),700);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.active.postMessage({t:'PING'},[ch.port2])})});
    result.afterClose=state;
  }
 }catch(e){result.error=String(e).slice(0,220)}
 finally{await context.close()}
 results.push(result);console.log('R256_SKIPWAITING '+JSON.stringify(result));
}
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{
  for(let [name,engine] of [['Chromium',chromium],['WebKit',webkit]]){
    let browser=await engine.launch({headless:true});
    try{for(let mode of ['waitUntil','unawaited','promise','sync']){
      variant=mode;
      for(let n=0;n<6;n++){run=n+1;await test(name,browser)}
    }}finally{await browser.close()}
  }
 }finally{await new Promise(r=>server.close(r))}
 let summary={};for(let r of results){let key=r.browser+'/'+r.variant;summary[key]??={total:0,activated:0,ack:0,afterClose:0};summary[key].total++;summary[key].activated+=+!!r.activated;summary[key].ack+=+(r.ack==='RECEIVED');summary[key].afterClose+=+(r.afterClose==='B')}
 console.log('R256_SKIPWAITING_SUMMARY '+JSON.stringify(summary));require('node:fs').writeFileSync('r256-skipwaiting-comparison.json',JSON.stringify({summary,results},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
