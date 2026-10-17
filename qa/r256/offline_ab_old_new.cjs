const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),{chromium,webkit}=require('playwright');
let root=process.cwd();const OLD='/tmp/ldc_r256_old',NEW=process.cwd(),results=[];
function put(label,x={}){let d={label,at:new Date().toISOString(),...x};results.push(d);console.log('R257_OFFLINE_AB '+JSON.stringify(d))}
let server=http.createServer((req,res)=>{let u=new URL(req.url,'http://127.0.0.1'),p=decodeURIComponent(u.pathname).replace(/^\/+/,'').replace(/^App-Test\//,'')||'index.html';let file=path.resolve(root,p);if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}fs.readFile(file,(e,b)=>{if(e){res.writeHead(404);res.end();return}res.writeHead(200,{'cache-control':'no-store','content-type':{'.html':'text/html','.js':'application/javascript','.mjs':'application/javascript','.json':'application/json','.css':'text/css','.woff2':'font/woff2','.png':'image/png'}[path.extname(file)]||'application/octet-stream'});res.end(b)})});
const wait=t=>new Promise(r=>setTimeout(r,t));
async function state(page){return await page.evaluate(async()=>{let reg=await navigator.serviceWorker.getRegistration().catch(()=>null),loading=document.querySelector('#loading');return {version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,stage:typeof bootStage!=='undefined'?bootStage:null,ready:loading?getComputedStyle(loading).display==='none':null,offline:typeof offlineUiState!=='undefined'?{state:offlineUiState.state,count:offlineUiState.completed,total:offlineUiState.total}:null,active:reg?.active?.state,controller:!!navigator.serviceWorker.controller,diag:document.querySelector('#boot-error-code')?.textContent||null}})}
async function poll(page,fn,t=18000){let lim=Date.now()+t,s;while(Date.now()<lim){s=await state(page);if(fn(s))return s;await wait(350)}return s;}
async function test(engine,label,which){
 root=which==='old'?OLD:NEW;
 let b=await engine.launch({headless:true}),ctx=await b.newContext({serviceWorkers:'allow'}),page=await ctx.newPage(),url='http://127.0.0.1:'+server.address().port+'/App-Test/';
 try{
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
  let init=await poll(page,x=>x.ready&&x.active==='activated',23000);
  put('ready',{engine:label,which,init});
  if(!init.ready)throw Error('not booted');
  await page.evaluate(async()=>await startOfflinePreparation());
  let offline=await poll(page,x=>['READY','ERROR','PARTIAL'].includes(x.offline?.state),160000);
  put('download',{engine:label,which,offline});
  if(offline?.offline?.state!=='READY'||offline.offline.count!==205)throw Error('offline cache not READY 205');
  await ctx.setOffline(true);
  try {
   await page.reload({waitUntil:'domcontentloaded',timeout:12000});
   put('offline_reload',{engine:label,which,result:'NAVIGATED',state:await poll(page,x=>x.ready||x.diag,9000)});
  }catch(e){put('offline_reload',{engine:label,which,result:'BROWSER_ERROR',error:String(e).slice(0,420)})}
  await page.close();page=await ctx.newPage();
  try{
   await page.goto(url,{waitUntil:'domcontentloaded',timeout:12000});
   put('offline_new_tab',{engine:label,which,result:'NAVIGATED',state:await poll(page,x=>x.ready||x.diag,9000)});
  }catch(e){put('offline_new_tab',{engine:label,which,result:'BROWSER_ERROR',error:String(e).slice(0,420)})}
 }catch(e){put('case_exception',{engine:label,which,error:String(e).slice(0,420)})}
 finally{await ctx.close();await b.close()}
}
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));try{for(let [name,browser] of [['Chromium',chromium],['WebKit',webkit]])for(let which of ['old','new'])await test(browser,name,which)}finally{await new Promise(r=>server.close(r));fs.writeFileSync('r257-offline-ab-results.json',JSON.stringify(results,null,2))}})().catch(e=>{console.error(e);process.exit(1)});
