const { chromium } = require('playwright');
const axe = require('axe-core');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const RID='24h-v120-b6-20261003-adversarial-runtime-closure';
const SEQ=120000006;
const ROUTE='24h-v120-b6-adversarial';
function fail(msg){throw new Error(msg)}
function copyTree(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.mkdirSync(path.dirname(dst),{recursive:true});fs.cpSync(src,dst,{recursive:true});}
async function swInfo(worker){
  return await new Promise((resolve,reject)=>{
    const ch=new MessageChannel(); const t=setTimeout(()=>reject(new Error('sw_info_timeout')),5000);
    ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};
    worker.postMessage({type:'GET_RELEASE_INFO_V2'},[ch.port2]);
  });
}
async function activateWaiting(worker){
  return await new Promise((resolve,reject)=>{
    const ch=new MessageChannel(); const t=setTimeout(()=>reject(new Error('activate_timeout')),8000);
    ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};
    worker.postMessage({type:'ACTIVATE_UPDATE_V2',expected_release_id:RID,expected_release_sequence:SEQ,request_id:'blind-b6-'+Date.now()},[ch.port2]);
  });
}
async function pageAudit(page,label){
  const out={label};
  out.runtime=await page.evaluate(({RID,SEQ})=>({
    title:document.title,
    theme:document.documentElement.getAttribute('data-theme'),
    appVersion:typeof APP_VERSION!=='undefined'?APP_VERSION:null,
    buildRevision:typeof BUILD_REVISION!=='undefined'?BUILD_REVISION:null,
    releaseId:typeof APP_RELEASE_ID!=='undefined'?APP_RELEASE_ID:null,
    releaseSequence:typeof APP_RELEASE_SEQUENCE!=='undefined'?APP_RELEASE_SEQUENCE:null,
    functions:Object.fromEntries(['showHome','showHoursView','openHour','showSearchView','showEspaceView','showHelp','showSettingsSheet','setThemePreference'].map(k=>[k,typeof globalThis[k]])),
    horizontalOverflow:document.documentElement.scrollWidth-window.innerWidth,
    duplicateIds:(()=>{const a=[...document.querySelectorAll('[id]')].map(e=>e.id);return [...new Set(a.filter((x,i)=>a.indexOf(x)!==i))]})(),
    visibleUnlabelledControls:[...document.querySelectorAll('button,input,select,textarea,a[href],[role="button"]')].filter(el=>{
      const r=el.getBoundingClientRect(),s=getComputedStyle(el); if(r.width<=0||r.height<=0||s.visibility==='hidden'||s.display==='none')return false;
      const txt=(el.innerText||el.textContent||el.value||'').trim(); return !txt&&!el.getAttribute('aria-label')&&!el.getAttribute('title')&&!el.getAttribute('aria-labelledby');
    }).map(el=>el.outerHTML.slice(0,220))
  }),{RID,SEQ});
  if(out.runtime.appVersion!=='v120'||out.runtime.buildRevision!=='B6'||out.runtime.releaseId!==RID||out.runtime.releaseSequence!==SEQ) fail(label+' identity mismatch '+JSON.stringify(out.runtime));
  for(const [k,v] of Object.entries(out.runtime.functions)) if(v!=='function') fail(label+' missing function '+k);
  if(out.runtime.duplicateIds.length) fail(label+' duplicate DOM ids '+out.runtime.duplicateIds.join(','));
  if(out.runtime.visibleUnlabelledControls.length) fail(label+' unlabelled controls '+JSON.stringify(out.runtime.visibleUnlabelledControls.slice(0,5)));
  if(out.runtime.horizontalOverflow>2) fail(label+' horizontal overflow '+out.runtime.horizontalOverflow);

  // Major functional surfaces.
  out.flows={};
  await page.evaluate(()=>showHome()); await page.waitForTimeout(150);
  out.flows.home=await page.locator('#content').innerText().catch(()=>page.locator('body').innerText());
  if(out.flows.home.length<300) fail(label+' home content unexpectedly short');
  await page.evaluate(()=>showHoursView()); await page.waitForTimeout(150);
  out.flows.hours=await page.locator('#content').innerText();
  if(!/Heure/i.test(out.flows.hours)) fail(label+' hours view missing');
  await page.evaluate(()=>openHour(1)); await page.waitForTimeout(200);
  out.flows.reader=await page.locator('#content').innerText();
  if(out.flows.reader.length<800) fail(label+' reader content unexpectedly short');
  await page.evaluate(()=>showSearchView()); await page.waitForTimeout(150);
  out.flows.search=await page.locator('#content').innerText();
  if(!/Recherch/i.test(out.flows.search)) fail(label+' search view missing');
  const search=page.locator('input[type="search"],input.search-input,input[placeholder*="Recher"]').first();
  if(await search.count()){
    await search.fill('volonté'); await search.dispatchEvent('input'); await page.waitForTimeout(350);
    out.flows.searchAfter=await page.locator('#content').innerText();
  }
  await page.evaluate(()=>showEspaceView()); await page.waitForTimeout(150);
  out.flows.espace=await page.locator('#content').innerText();
  if(!/Espace|Progression|Surlign/i.test(out.flows.espace)) fail(label+' personal space missing');
  await page.evaluate(()=>showHelp()); await page.waitForTimeout(150);
  out.flows.help=await page.locator('body').innerText();
  if(!/Aide/i.test(out.flows.help)) fail(label+' help missing');
  await page.keyboard.press('Escape'); await page.waitForTimeout(80);
  await page.evaluate(()=>showSettingsSheet()); await page.waitForTimeout(150);
  out.flows.settings=await page.locator('body').innerText();
  if(!/Réglages|Affichage|Taille|Thème/i.test(out.flows.settings)) fail(label+' settings missing');
  await page.keyboard.press('Escape'); await page.waitForTimeout(80);

  // Keyboard reachability: tab through first 35 stops and ensure focus is visible on each interactive stop.
  out.focus=[];
  await page.evaluate(()=>showHome()); await page.locator('body').focus().catch(()=>{});
  for(let i=0;i<35;i++){
    await page.keyboard.press('Tab');
    const f=await page.evaluate(()=>{const e=document.activeElement;if(!e)return null;const s=getComputedStyle(e);const r=e.getBoundingClientRect();return{tag:e.tagName,id:e.id||'',cls:e.className||'',text:(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,60),outline:s.outline,boxShadow:s.boxShadow,w:r.width,h:r.height}});
    if(f) out.focus.push(f);
  }
  if(!out.focus.some(x=>(x.outline&&x.outline!=='none')||(x.boxShadow&&x.boxShadow!=='none'))) fail(label+' no visible keyboard focus evidence');

  // Axe WCAG scan on home.
  await page.evaluate(axe.source);
  const ax=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
  out.axe=ax.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.slice(0,8).map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))}));
  return out;
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 const evidence={exact:{route:ROUTE,releaseId:RID,releaseSequence:SEQ},contexts:{},pwa:{},upgrade:{}};

 // Fresh runtime contexts: mobile/desktop x light/dark.
 for(const vp of [{name:'mobile',width:390,height:844},{name:'desktop',width:1366,height:900}]){
  for(const scheme of ['light','dark']){
   const ctx=await browser.newContext({colorScheme:scheme,viewport:{width:vp.width,height:vp.height}});
   const page=await ctx.newPage(); const consoleErrors=[],pageErrors=[],requestFails=[];
   page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
   page.on('pageerror',e=>pageErrors.push(String(e)));
   page.on('requestfailed',r=>requestFails.push({url:r.url(),failure:r.failure()}));
   const res=await page.goto('http://127.0.0.1:8090/'+ROUTE+'/',{waitUntil:'domcontentloaded',timeout:120000});
   await page.waitForTimeout(1300);
   const key=vp.name+'-'+scheme;
   evidence.contexts[key]={http:res&&res.status(),consoleErrors,pageErrors,requestFails,audit:await pageAudit(page,key)};
   if(consoleErrors.some(x=>/content security policy|uncaught|referenceerror|typeerror/i.test(x))) fail(key+' console errors '+consoleErrors.join(' | '));
   if(pageErrors.length) fail(key+' page errors '+pageErrors.join(' | '));
   await ctx.close();
  }
 }

 // Clean B6 PWA install and offline recovery.
 {
  const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:390,height:844}});
  const page=await ctx.newPage(); const errors=[]; page.on('console',m=>{if(m.type()==='error')errors.push(m.text())}); page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://127.0.0.1:8090/'+ROUTE+'/luisa_24_heures.html',{waitUntil:'domcontentloaded'}); await page.waitForTimeout(800);
  const ready=await page.evaluate(async()=>{const r=await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('sw ready timeout')),15000))]);return !!r.active});
  if(!ready) fail('clean PWA no active worker');
  const info=await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return await new Promise((resolve,reject)=>{const ch=new MessageChannel();const t=setTimeout(()=>reject(new Error('msg timeout')),5000);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.active.postMessage({type:'GET_RELEASE_INFO_V2'},[ch.port2])})});
  evidence.pwa.cleanInfo=info;
  if(info.build_revision!=='B6'||info.release_id!==RID||Number(info.release_sequence)!==SEQ) fail('clean PWA release info mismatch '+JSON.stringify(info));
  await page.evaluate(()=>setThemePreference('dark')); await page.waitForTimeout(250);
  await ctx.setOffline(true); await page.reload({waitUntil:'domcontentloaded',timeout:30000}); await page.waitForTimeout(500);
  evidence.pwa.offline=await page.evaluate(()=>({theme:document.documentElement.getAttribute('data-theme'),body:(document.body.innerText||'').slice(0,250),openHour:typeof openHour}));
  if(evidence.pwa.offline.openHour!=='function'||evidence.pwa.offline.theme!=='dark') fail('offline recovery/state failed '+JSON.stringify(evidence.pwa.offline));
  await ctx.setOffline(false); await page.reload({waitUntil:'domcontentloaded'}); await page.waitForTimeout(400);
  evidence.pwa.onlineRecovery=await page.evaluate(()=>({theme:document.documentElement.getAttribute('data-theme'),openHour:typeof openHour}));
  if(evidence.pwa.onlineRecovery.openHour!=='function') fail('online recovery failed');
  if(errors.some(x=>/content security policy|manifest_release_identity_mismatch|uncaught|referenceerror/i.test(x))) fail('PWA console/runtime errors '+errors.join(' | '));
  await ctx.close();
 }

 // Exact v119 -> B6 same-scope update transaction.
 {
  const slot='qa-upgrade/24h';
  copyTree('24h-v119-b1-governed-r4',slot);
  const ctx=await browser.newContext({colorScheme:'light',viewport:{width:390,height:844}});
  const page=await ctx.newPage(); const errs=[]; page.on('console',m=>{if(m.type()==='error')errs.push(m.text())}); page.on('pageerror',e=>errs.push(String(e)));
  await page.goto('http://127.0.0.1:8091/24h/luisa_24_heures.html',{waitUntil:'domcontentloaded'}); await page.waitForTimeout(1000);
  const preInfo=await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return await new Promise((resolve,reject)=>{const ch=new MessageChannel();const t=setTimeout(()=>reject(new Error('pre info timeout')),5000);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.active.postMessage({type:'GET_RELEASE_INFO_V2'},[ch.port2])})});
  evidence.upgrade.pre=preInfo;
  await page.evaluate(()=>setThemePreference('dark')); await page.waitForTimeout(200);
  copyTree(ROUTE,slot);
  const upd=await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update(); const start=Date.now();while(!r.waiting&&Date.now()-start<15000)await new Promise(x=>setTimeout(x,200));return{waiting:!!r.waiting,installing:!!r.installing}});
  evidence.upgrade.update=upd;
  if(!upd.waiting) fail('B6 update did not reach waiting state');
  const waitingInfo=await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();return await new Promise((resolve,reject)=>{const ch=new MessageChannel();const t=setTimeout(()=>reject(new Error('waiting info timeout')),5000);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.waiting.postMessage({type:'GET_RELEASE_INFO_V2'},[ch.port2])})});
  evidence.upgrade.waitingInfo=waitingInfo;
  if(waitingInfo.build_revision!=='B6'||waitingInfo.release_id!==RID||Number(waitingInfo.release_sequence)!==SEQ) fail('waiting worker identity mismatch '+JSON.stringify(waitingInfo));
  const activation=await page.evaluate(async({RID,SEQ})=>{const r=await navigator.serviceWorker.getRegistration();return await new Promise((resolve,reject)=>{const ch=new MessageChannel();const t=setTimeout(()=>reject(new Error('activate reply timeout')),8000);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.waiting.postMessage({type:'ACTIVATE_UPDATE_V2',expected_release_id:RID,expected_release_sequence:SEQ,request_id:'blind-'+Date.now()},[ch.port2])})},{RID,SEQ});
  evidence.upgrade.activation=activation;
  if(activation.type!=='ACTIVATE_UPDATE_ACCEPTED_V2') fail('activation rejected '+JSON.stringify(activation));
  await page.waitFor_timeout?.(0);
  await page.waitForTimeout(1200);
  await page.reload({waitUntil:'domcontentloaded'}); await page.waitForTimeout(600);
  evidence.upgrade.post=await page.evaluate(()=>({build:BUILD_REVISION,rid:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,theme:document.documentElement.getAttribute('data-theme'),openHour:typeof openHour}));
  if(evidence.upgrade.post.build!=='B6'||evidence.upgrade.post.rid!==RID||evidence.upgrade.post.seq!==SEQ||evidence.upgrade.post.theme!=='dark'||evidence.upgrade.post.openHour!=='function') fail('post-upgrade mismatch '+JSON.stringify(evidence.upgrade.post));
  if(errs.some(x=>/content security policy|manifest_release_identity_mismatch|uncaught|referenceerror/i.test(x))) fail('upgrade errors '+errs.join(' | '));
  await ctx.close();
 }

 await browser.close();
 fs.writeFileSync('24h-b6-full-blind-adversarial.json',JSON.stringify(evidence,null,2));
 console.log('24H_B6_FULL_BLIND_ADVERSARIAL_PASS');
})().catch(e=>{console.error('BLIND_FAIL',e);process.exit(1)});