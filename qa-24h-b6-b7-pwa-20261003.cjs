const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
const pred='24h-v120-b6-darkmode',succ='24h-v120-b7-darkmode',dst=path.join('qa-fresh-upgrade','24h');
function copy(a,b){fs.rmSync(b,{recursive:true,force:true});fs.cpSync(a,b,{recursive:true});}
(async()=>{
 copy(pred,dst); const browser=await chromium.launch({headless:true}); const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:390,height:844}});
 let p=await ctx.newPage(); const errs=[];p.on('pageerror',e=>errs.push(String(e)));
 const url='http://127.0.0.1:8080/qa-fresh-upgrade/24h/';
 let r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});if(!r||!r.ok())throw new Error('predecessor load');
 await p.waitForTimeout(1500);await p.evaluate(()=>localStorage.setItem('APP_GOV_SENTINEL','persist-b7'));
 const pre=await p.evaluate(async()=>{const v=await fetch('version.json',{cache:'no-store'}).then(r=>r.json());let reg=null;try{reg=await navigator.serviceWorker.ready}catch(e){}return{release_id:v.release_id,seq:v.release_sequence,sw:!!reg,caches:await caches.keys()}});
 copy(succ,dst);
 const upd=await p.evaluate(async()=>{const reg=await navigator.serviceWorker.getRegistration();if(!reg)return{registration:false};await reg.update();await new Promise(r=>setTimeout(r,1800));return{registration:true,installing:!!reg.installing,waiting:!!reg.waiting,active:!!reg.active}});
 await p.close();await new Promise(r=>setTimeout(r,1200));p=await ctx.newPage();p.on('pageerror',e=>errs.push(String(e)));
 r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});if(!r||!r.ok())throw new Error('successor load');await p.waitForTimeout(1200);
 const post=await p.evaluate(async()=>({sentinel:localStorage.getItem('APP_GOV_SENTINEL'),version:await fetch('version.json',{cache:'no-store'}).then(r=>r.json()),caches:await caches.keys(),controller:!!navigator.serviceWorker.controller}));
 if(post.sentinel!=='persist-b7'||post.version.release_sequence!==120000007)throw new Error('online successor/state mismatch');
 await ctx.setOffline(true);await p.reload({waitUntil:'domcontentloaded',timeout:30000});await p.waitForTimeout(500);
 const off=await p.evaluate(async()=>{let version=null;try{version=await fetch('version.json').then(r=>r.json())}catch(e){}return{sentinel:localStorage.getItem('APP_GOV_SENTINEL'),version,title:document.title,body:(document.body.innerText||'').slice(0,160)}});
 if(off.sentinel!=='persist-b7'||!off.version||off.version.release_sequence!==120000007||!off.title||!off.body)throw new Error('offline successor/state mismatch');
 console.log(JSON.stringify({pre,upd,post:{sentinel:post.sentinel,release_id:post.version.release_id,seq:post.version.release_sequence,caches:post.caches,controller:post.controller},off:{sentinel:off.sentinel,release_id:off.version.release_id,seq:off.version.release_sequence,title:off.title},pageErrors:errs},null,2));
 if(errs.length)throw new Error('page errors '+errs.join(';'));await ctx.close();await browser.close();console.log('B6_B7_PWA_OFFLINE_STATE_PASS');
})().catch(e=>{console.error(e);process.exit(1)});