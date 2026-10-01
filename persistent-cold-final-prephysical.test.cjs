const { chromium } = require('playwright');
const fs=require('fs'), path=require('path');
const specs={
  h24:{url:'https://louisriv26.github.io/App-Test/24h-v119-b1-prephysical/',expect:{app:'v119'}},
  ldc:{url:'https://louisriv26.github.io/App-Test/ldc-v132-b1-prephysical/',expect:{app:'132',pub:'132'}},
  lettres:{url:'https://louisriv26.github.io/App-Test/lettres-v2.10-b1-prephysical/',expect:{app:'2.10',letters:136}},
  mjv:{url:'https://louisriv26.github.io/App-Test/marie-v46/',expect:{app:'46'}},
  hub:{url:'https://louisriv26.github.io/Hub---Github/',expect:{hubVersion:'1.0.6',cards:4}}
};
const report={generated_at:new Date().toISOString(),candidate_set:'24H_v119__LDC_v132__LETTRES_v2.10__MJV_v46__HUB_v1.0.6',apps:{},overall:'UNKNOWN'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function probe(page,key){
  return page.evaluate(async key=>{
    const out={body:document.body.innerText.length};
    try{out.app=typeof APP_VERSION!=='undefined'?String(APP_VERSION):null}catch(_){}
    try{out.pub=typeof PUBLIC_VERSION!=='undefined'?String(PUBLIC_VERSION):null}catch(_){}
    try{out.letters=typeof CORPUS!=='undefined'&&Array.isArray(CORPUS)?CORPUS.length:null}catch(_){}
    out.cards=document.querySelectorAll('.app-card').length;
    if(key==='hub'){
      try{const r=await fetch('./version.json',{cache:'no-store'});if(r.ok){const v=await r.json();out.hubVersion=String(v.app_version||v.version||'')}}catch(_){}
    }
    let sw=null;
    if('serviceWorker' in navigator){
      try{const reg=await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout')),12000))]);sw={active:!!reg.active,controller:!!navigator.serviceWorker.controller,scope:reg.scope};}
      catch(e){sw={error:String(e),controller:!!navigator.serviceWorker.controller};}
    }
    out.sw=sw; return out;
  },key);
}
function matches(x,e,key){
  if(e.app && x.app!==e.app)return false;
  if(e.pub && x.pub!==e.pub)return false;
  if(e.letters && x.letters!==e.letters)return false;
  if(e.cards && x.cards!==e.cards)return false;
  if(e.hubVersion && x.hubVersion!==e.hubVersion)return false;
  if(key!=='hub' && (!x.sw||!x.sw.active))return false;
  return x.body>(key==='ldc'?50:100);
}
async function onlineSeed(key,s,dir){
  const c=await chromium.launchPersistentContext(dir,{headless:true,serviceWorkers:'allow',viewport:{width:1180,height:850}});
  const p=await c.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(String(e)));
  let status=null,nav_error=null;
  try{const r=await p.goto(s.url,{waitUntil:'domcontentloaded',timeout:60000});status=r&&r.status();}catch(e){nav_error=String(e);}
  await sleep(1800);
  let pr=await probe(p,key);
  if(pr.sw&&pr.sw.active&&!pr.sw.controller){try{await p.reload({waitUntil:'domcontentloaded',timeout:60000});await sleep(1200);pr=await probe(p,key);}catch(e){errors.push('reload:'+String(e));}}
  await c.close();
  return {status,nav_error,errors,probe:pr,pass:status===200&&matches(pr,s.expect,key)};
}
async function offlineCold(key,s,dir,round){
  const c=await chromium.launchPersistentContext(dir,{headless:true,serviceWorkers:'allow',viewport:{width:1180,height:850}});
  await c.setOffline(true);
  const p=await c.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(String(e)));
  let nav_ok=true,nav_error=null;
  try{await p.goto(s.url,{waitUntil:'domcontentloaded',timeout:30000});}catch(e){nav_ok=false;nav_error=String(e);}
  await sleep(1200);
  let pr={};try{pr=await probe(p,key);}catch(e){pr={error:String(e)}}
  await c.close();
  return {round,nav_ok,nav_error,errors,probe:pr,pass:nav_ok&&matches(pr,s.expect,key)};
}
(async()=>{
  for(const [key,s] of Object.entries(specs)){
    const dir=path.join(process.cwd(),'.final-cold-profile-'+key);fs.rmSync(dir,{recursive:true,force:true});
    const online=await onlineSeed(key,s,dir);
    const cold1=await offlineCold(key,s,dir,1);
    const cold2=await offlineCold(key,s,dir,2);
    report.apps[key]={online,cold1,cold2,pass:online.pass&&cold1.pass&&cold2.pass};
  }
  report.overall=Object.values(report.apps).every(x=>x.pass)?'PASS':'FAIL';
  fs.writeFileSync('persistent-cold-final-prephysical-results.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  if(report.overall!=='PASS')process.exitCode=1;
})().catch(e=>{report.overall='HARNESS_ERROR';report.error=String(e&&e.stack||e);fs.writeFileSync('persistent-cold-final-prephysical-results.json',JSON.stringify(report,null,2)+'\n');console.error(e);process.exitCode=2;});
