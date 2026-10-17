const {chromium,webkit}=require('playwright');
const fs=require('node:fs'),crypto=require('node:crypto');
const ROOT='https://louisriv26.github.io/App-Test/';
const manifest=JSON.parse(fs.readFileSync('PACKAGE_MANIFEST_SHA256.json','utf8'));
const entries=new Map(manifest.files.map(x=>[x.path,x]));
const results=[];
function log(tag,info={}){const obj={tag,...info};results.push(obj);console.log('R257_HOSTED '+JSON.stringify(obj))}
async function wait(ms){return new Promise(r=>setTimeout(r,ms))}
const digest=buf=>crypto.createHash('sha256').update(buf).digest('hex');
async function get(path,force=false){
 const u=new URL(path,ROOT);if(force)u.searchParams.set('r257qa',Date.now().toString(36));
 const r=await fetch(u,{cache:'no-store',headers:{'Cache-Control':'no-cache'}});
 if(!r.ok)throw new Error('HTTP '+r.status+' '+u.href);
 return Buffer.from(await r.arrayBuffer());
}
async function checkPublish(){
 let matched=false;
 for(let i=0;i<75;i++){
  try{let data=JSON.parse((await get('version.json',true)).toString());
   if(data.app_version==='v2.19.142.46-R1B-UNIFIED'){matched=true;break;}
   if(i%6===0)log('wait_publication',{attempt:i+1,actual:data.app_version});
  }catch(e){if(i%6===0)log('version_wait_error',{error:String(e)})}
  await wait(8000);
 }
 if(!matched)throw new Error('GitHub Pages did not serve v142.46 in 10 minutes');
 const paths=['index.html','offline_manifest.json','sw.js','version.json'];
 for(let path of paths){
   const buf=await get(path,true),entry=entries.get(path);
   if(!entry)throw new Error('Not in package manifest: '+path);
   const actual=digest(buf),expected=entry.sha256;
   log('published_file',{path,bytes:buf.byteLength,hash:actual,expected,ok:actual===expected});
   if(actual!==expected)throw new Error('hosted mismatch '+path);
 }
 const pub=JSON.parse((await get('offline_manifest.json',true)).toString());
 if(pub.asset_count!==205||pub.content_binding_sha256!=='c6d295844181613e12fb121a9d803e5b8d801e63a084ebd790439b914cde14fd')throw new Error('offline revision incorrect');
 log('published_static_assets',{status:'PASS',count:4});
}
async function state(page){
 return await page.evaluate(async()=>{
  const el=document.getElementById('loading');
  const r=await navigator.serviceWorker.getRegistration().catch(()=>null);
  const sw=navigator.serviceWorker.controller||r?.active;
  let revision=null;
  if(sw) revision=await new Promise(resolve=>{const ch=new MessageChannel();const t=setTimeout(()=>resolve('TIMEOUT'),900);
   ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data?.version||null)};
   try{sw.postMessage({type:'LDC_GET_VERSION'},[ch.port2])}catch(e){clearTimeout(t);resolve('ERROR:'+String(e))}});
  const off=typeof offlineUiState!=='undefined'?offlineUiState:null;
  return {app:typeof APP_VERSION!=='undefined'?APP_VERSION:null,stage:typeof bootStage!=='undefined'?bootStage:null,
     loading:el?getComputedStyle(el).display!=='none':null,
     diagnostic:document.getElementById('boot-error-code')?.textContent||null,
     active:r?.active?.state||null,waiting:r?.waiting?.state||null,revision,
     offline:{state:off?.state||null,completed:off?.completed||0,total:off?.total||0},
     home:!!document.getElementById('home-screen'),
     body:document.body?.innerText?.slice(0,150)||''};
 })
}
async function until(page,fn,ms=45000){let end=Date.now()+ms,s;do{s=await state(page);if(fn(s))return s;await wait(300)}while(Date.now()<end);return s}
async function browserSmoke(engine,name){
 const browser=await engine.launch({headless:true});
 const context=await browser.newContext({serviceWorkers:'allow',viewport:{width:430,height:850}});
 const page=await context.newPage();
 const errors=[];
 page.on('pageerror',e=>errors.push(String(e).slice(0,200)));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text().slice(0,200))});
 try{
  const response=await page.goto(ROOT+'?r257_hosted_fresh='+Date.now(),{waitUntil:'domcontentloaded',timeout:65000});
  let st=await until(page,s=>s.loading===false||s.diagnostic,70000);
  log('browser_open',{engine:name,http:response?.status(),state:st});
  if(st.diagnostic||st.loading||st.app!=='v2.19.142.46-R1B-UNIFIED')throw Error('boot failed '+JSON.stringify(st));
  st=await until(page,s=>s.revision?.includes('142.46'),30000);
  log('browser_new_worker',{engine:name,state:st});
  if(st.revision!=='ldc-v2.19.142.46-r1b-unified')throw Error('SW activation failed');
  await page.evaluate(async()=>await startOfflinePreparation());
  st=await until(page,s=>['READY','ERROR','PARTIAL'].includes(s.offline.state),140000);
  log('browser_offline_prep',{engine:name,state:st});
  if(st.offline.state!=='READY'||st.offline.completed!==205)throw Error('offline prep failed');
  await page.evaluate(async()=>{await dbPut('settings',{key:'r257_hosted_qa_synthetic',val:{ok:true},ts:Date.now()})});
  const marker=await page.evaluate(async()=>await dbGet('settings','r257_hosted_qa_synthetic'));
  log('browser_synthetic_storage',{engine:name,ok:marker?.val?.ok===true});
  if(marker?.val?.ok!==true)throw Error('storage failed');
  // Do not call any destructive reset or unregister during test.
  await page.reload({waitUntil:'domcontentloaded',timeout:65000});
  st=await until(page,s=>s.loading===false||s.diagnostic,70000);
  log('browser_reload',{engine:name,state:st});
  if(st.diagnostic||st.loading)throw Error('reload failed');
  log('browser_errors',{engine:name,count:errors.length,samples:errors.slice(0,7)});
  if(errors.length)throw Error('browser JavaScript errors');
 }catch(e){log('browser_fail',{engine:name,error:String(e)});throw e}
 finally{await context.close();await browser.close()}
}
(async()=>{
 let ok=false;try{
  await checkPublish();
  await browserSmoke(chromium,'Chromium');
  await browserSmoke(webkit,'WebKit');
  ok=true;
 }catch(e){log('FAIL',{error:String(e)})}
 finally{fs.writeFileSync('r257-hosted-qa.json',JSON.stringify({ok,results},null,2))}
 if(!ok)process.exitCode=1;
})();
