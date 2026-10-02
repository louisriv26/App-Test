const {chromium}=require('playwright'); const fs=require('fs'), path=require('path');
const cases=[
 {name:'24H',pred:'24h-v119-b1-governed-r4',succ:'24h-v120-b4-darkmode',slot:'24h'},
 {name:'LDC',pred:'ldc-v135-r8-governed-r7',succ:'ldc-v136-r9-darkmode',slot:'ldc'},
 {name:'Lettres',pred:'lettres-v2.10-b1-prephysical',succ:'lettres-v2.12-b1-darkmode',slot:'lettres'},
 {name:'Marie',pred:'marie-v46',succ:'marie-v47-b1-darkmode',slot:'marie'}
];
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
(async()=>{
 const browser=await chromium.launch({headless:true}); const out={generated_at:new Date().toISOString(),cases:{}};
 for(const c of cases){
   const dst=path.join('qa-upgrade',c.slot); copy(c.pred,dst);
   const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:900,height:700}});
   let p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
   const url='http://127.0.0.1:8081/'+c.slot+'/';
   let r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000}); if(!r||!r.ok())throw new Error(c.name+' predecessor load');
   await p.waitForTimeout(1200);
   const pre=await p.evaluate(async(name)=>{
     localStorage.setItem('APP_GOV_SENTINEL','persist-'+name);
     let reg=null; try{reg=await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('sw-ready-timeout')),10000))])}catch(e){}
     return {sentinel:localStorage.getItem('APP_GOV_SENTINEL'),title:document.title,sw:!!reg,caches:await caches.keys()};
   },c.name);
   copy(c.succ,dst);
   const upd=await p.evaluate(async()=>{
     const reg=await navigator.serviceWorker.getRegistration(); if(!reg)return {registration:false};
     try{await reg.update()}catch(e){return {registration:true,updateError:String(e)}}
     await new Promise(r=>setTimeout(r,1800));
     return {registration:true,installing:!!reg.installing,waiting:!!reg.waiting,active:!!reg.active,caches:await caches.keys()};
   });
   await p.close(); await new Promise(r=>setTimeout(r,1200));
   p=await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message));
   r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000}); if(!r||!r.ok())throw new Error(c.name+' successor load');
   await p.waitForTimeout(1200);
   const post=await p.evaluate(async()=>({sentinel:localStorage.getItem('APP_GOV_SENTINEL'),title:document.title,caches:await caches.keys(),controller:!!navigator.serviceWorker.controller,body:(document.body.innerText||'').trim().slice(0,200)}));
   if(post.sentinel!=='persist-'+c.name) throw new Error(c.name+' state sentinel lost');
   if(!post.title||!post.body) throw new Error(c.name+' successor shell empty');
   await ctx.setOffline(true);
   await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForTimeout(500);
   const off=await p.evaluate(()=>({title:document.title,body:(document.body.innerText||'').trim().slice(0,200),sentinel:localStorage.getItem('APP_GOV_SENTINEL')}));
   if(!off.title||!off.body||off.sentinel!=='persist-'+c.name)throw new Error(c.name+' offline/state failure');
   out.cases[c.name]={pre,update:upd,post,offline:off,pageErrors:errs};
   await ctx.close();
 }
 await browser.close(); fs.writeFileSync('successor-pwa-offline-state-r2-results.json',JSON.stringify(out,null,2)); console.log('SUCCESSOR_PWA_OFFLINE_STATE_PASS');
})().catch(e=>{console.error(e);process.exit(1)});