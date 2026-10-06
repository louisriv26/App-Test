const { chromium }=require('playwright');
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=process.cwd(), RUN=path.join(ROOT,'.upgrade-runtime');
const specs={
 h24:{old:'upgrade-24h-v119',final:'24h-v119-b1-governed-r4',route:'h24',oldV:'v111.0',newV:'v119'},
 ldc:{old:'upgrade-ldc-v132',final:'ldc-v131-r5-governed-r4',route:'ldc',oldV:'v2.19.128-R1B-UX-ACCESS-R2',newV:'v2.19.131-R1B-UX-ACCESS-R5'},
 lettres:{old:'upgrade-lettres-v2-10',final:'lettres-v2.9-b1-governed-r4',route:'lettres',oldV:'2.4',newV:'2.9'}
};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function copyTree(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
async function identity(p,key){
 return p.evaluate(key=>{
  let app=null,pub=null;
  try{app=typeof APP_VERSION!=='undefined'?String(APP_VERSION):null}catch(_){}
  try{pub=typeof PUBLIC_VERSION!=='undefined'?String(PUBLIC_VERSION):null}catch(_){}
  return {app,pub,body:document.body.innerText.length,controller:navigator.serviceWorker&&navigator.serviceWorker.controller&&navigator.serviceWorker.controller.scriptURL||null};
 },key);
}
async function seed(p){
 return p.evaluate(async()=>{
  localStorage.setItem('__prephysical_upgrade_sentinel__','keep-me');
  await new Promise((res,rej)=>{const q=indexedDB.open('__prephysical_upgrade_sentinel__',1);q.onupgradeneeded=()=>q.result.createObjectStore('x');q.onsuccess=()=>{const db=q.result,tx=db.transaction('x','readwrite');tx.objectStore('x').put('keep-me','k');tx.oncomplete=()=>{db.close();res()};tx.onerror=()=>rej(tx.error)};q.onerror=()=>rej(q.error)});
  return true;
 });
}
async function verifyState(p){
 return p.evaluate(async()=>{
  const ls=localStorage.getItem('__prephysical_upgrade_sentinel__');
  const idb=await new Promise(res=>{const q=indexedDB.open('__prephysical_upgrade_sentinel__');q.onsuccess=()=>{const db=q.result;try{const tx=db.transaction('x','readonly'),g=tx.objectStore('x').get('k');g.onsuccess=()=>{db.close();res(g.result)};g.onerror=()=>{db.close();res(null)}}catch(_){db.close();res(null)}};q.onerror=()=>res(null)});
  return {localStorage:ls,indexedDB:idb};
 });
}
async function waitReady(p){
 await p.evaluate(async()=>{if('serviceWorker'in navigator){await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('sw ready timeout')),15000))])}});
}
async function upgrade(p){
 return p.evaluate(async()=>{
  const reg=await navigator.serviceWorker.getRegistration();
  if(!reg)return {ok:false,reason:'no registration'};
  await reg.update();
  const until=Date.now()+15000;
  while(!reg.waiting && Date.now()<until){await new Promise(r=>setTimeout(r,250));await reg.update().catch(()=>{})}
  const w=reg.waiting||reg.installing;
  if(w){
    const ctrl=new Promise(res=>navigator.serviceWorker.addEventListener('controllerchange',()=>res(true),{once:true}));
    w.postMessage({type:'SKIP_WAITING'});
    await Promise.race([ctrl,new Promise(r=>setTimeout(()=>r(false),10000))]);
  }
  return {ok:true,waiting:!!reg.waiting,active:reg.active&&reg.active.scriptURL,controller:navigator.serviceWorker.controller&&navigator.serviceWorker.controller.scriptURL};
 });
}
(async()=>{
 fs.rmSync(RUN,{recursive:true,force:true});fs.mkdirSync(RUN,{recursive:true});
 for(const [k,s] of Object.entries(specs))copyTree(path.join(ROOT,s.old),path.join(RUN,s.route));
 const server=cp.spawn('python3',['-m','http.server','8765','--bind','127.0.0.1','--directory',RUN],{stdio:'ignore'});
 await sleep(1200);
 const browser=await chromium.launch({headless:true});
 const report={generated_at:new Date().toISOString(),apps:{},overall:'UNKNOWN'};
 try{
  for(const [k,s] of Object.entries(specs)){
    const ctx=await browser.newContext({serviceWorkers:'allow'}), p=await ctx.newPage(), errors=[];p.on('pageerror',e=>errors.push(String(e)));
    const url='http://127.0.0.1:8765/'+s.route+'/';
    const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:60000});await sleep(900);await waitReady(p);if(!navigator){}
    if(!(await p.evaluate(()=>!!navigator.serviceWorker.controller))){await p.reload({waitUntil:'domcontentloaded',timeout:60000});await sleep(600);}
    const before=await identity(p,k);await seed(p);
    copyTree(path.join(ROOT,s.final),path.join(RUN,s.route));await sleep(500);
    const activation=await upgrade(p);
    await p.close();
    const p2=await ctx.newPage();const errors2=[];p2.on('pageerror',e=>errors2.push(String(e)));
    let r2=null,navError=null;
    try{r2=await p2.goto(url+'?upgrade='+Date.now(),{waitUntil:'domcontentloaded',timeout:45000});}catch(e){navError=String(e);}
    await sleep(1200);try{await waitReady(p2)}catch(e){errors2.push(String(e))}
    const after=await identity(p2,k), state=await verifyState(p2);
    const beforeOk=before.app===s.oldV;
    const afterOk=k==='ldc'?(after.app===s.newV||after.pub===s.newV):after.app===s.newV;
    const pass=r&&r.status()===200&&r2&&r2.status()===200&&beforeOk&&afterOk&&state.localStorage==='keep-me'&&state.indexedDB==='keep-me'&&!errors.length&&!errors2.length;
    report.apps[k]={url,status:r&&r.status(),before,activation,after_status:r2&&r2.status(),navError,after,state,errors:[...errors,...errors2],pass};
    await ctx.close();
  }
 } finally {await browser.close();server.kill('SIGTERM');}
 report.overall=Object.values(report.apps).every(x=>x.pass)?'PASS':'FAIL';
 fs.writeFileSync('synthetic-upgrade-final-prephysical-results.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));if(report.overall!=='PASS')process.exitCode=1;
})().catch(e=>{const x={generated_at:new Date().toISOString(),overall:'HARNESS_ERROR',error:String(e&&e.stack||e)};fs.writeFileSync('synthetic-upgrade-final-prephysical-results.json',JSON.stringify(x,null,2)+'\\n');console.error(e);process.exitCode=2});
