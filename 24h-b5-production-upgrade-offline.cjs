
const {chromium}=require('playwright');
const fs=require('fs'), path=require('path');
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
const pred='24h-v119-b1-governed-r4', succ='24h-v120-b5-blind-repair', dst=path.join('qa-24h-upgrade','app');
const url='http://127.0.0.1:8085/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),pred,succ,steps:{}};
(async()=>{
  copy(pred,dst);
  const browser=await chromium.launch({headless:true});
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  let p=await ctx.newPage(); const consoleErrors=[],pageErrors=[];
  p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
  p.on('pageerror',e=>pageErrors.push(String(e.message||e)));
  let r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000}); if(!r||!r.ok())throw new Error('predecessor_http');
  await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v119'&&typeof buildPersonalSnapshotFromState==='function',null,{timeout:30000});
  await p.evaluate(async()=>{
    localStorage.setItem('APP_GOV_SENTINEL','24H-B5-UPGRADE');
    await setThemePreference('dark');
    await changeFontSize('xlarge');
    openHour(3);
    await new Promise(r=>setTimeout(r,450));
    const ok=await flushAndVerifyPersonalStateForUpdate(4000);
    if(!ok) throw new Error('predecessor_state_flush_failed');
  });
  const pre=await p.evaluate(async()=>{
    const reg=await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('sw_ready_timeout')),12000))]);
    const info=await queryWorkerRelease(reg.active);
    const snap=buildPersonalSnapshotFromState();
    return {identity:{APP_VERSION,BUILD_REVISION,APP_RELEASE_ID,APP_RELEASE_SEQUENCE},worker:info,snapshot:{themePreference:snap.themePreference,fontLevel:snap.fontLevel,lastHour:snap.lastHour},sentinel:localStorage.getItem('APP_GOV_SENTINEL'),caches:await caches.keys()};
  });
  out.steps.pre=pre;
  if(pre.identity.APP_VERSION!=='v119')throw new Error('pre_version_not_v119');
  if(!pre.worker||pre.worker.version!=='v119')throw new Error('pre_worker_not_v119');
  if(pre.snapshot.themePreference!=='dark'||pre.snapshot.fontLevel!=='xlarge'||String(pre.snapshot.lastHour)!=='3')throw new Error('pre_state_not_committed');

  copy(succ,dst);
  const prep=await p.evaluate(async()=>{
    const ok=await checkForUpdate(true,'blind-upgrade');
    await new Promise(r=>setTimeout(r,250));
    const pu=_preparedUpdate;
    return {checkResult:ok,prepared:!!pu,mode:pu&&pu.mode,remote:pu&&pu.remote?{sequence:pu.remote.sequence,version:pu.remote.version,releaseId:pu.remote.releaseId,shellHash:pu.remote.shellHash}:null,worker:pu&&pu.worker?await queryWorkerRelease(pu.worker):null,status:document.getElementById('updateCheckStatus')?.textContent||''};
  });
  out.steps.prepared=prep;
  if(!prep.prepared||prep.mode!=='waiting')throw new Error('successor_not_prepared_waiting');
  if(!prep.worker||prep.worker.releaseId!=='24h-v120-b5-20261002-blind-adversarial-repair'||prep.worker.version!=='v120')throw new Error('prepared_worker_identity_wrong');

  await p.evaluate(()=>{refreshAppForUpdate(); return true;});
  await p.waitForURL(u=>u.href.includes('lp_update_tx=')&&u.pathname.endsWith('/luisa_24_heures.html'),{timeout:30000});
  await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120'&&BUILD_REVISION==='B5',null,{timeout:30000});
  await p.waitForTimeout(1000);
  const post=await p.evaluate(async()=>{
    const reg=await navigator.serviceWorker.ready; const info=await queryWorkerRelease(reg.active); const snap=buildPersonalSnapshotFromState();
    return {identity:{APP_VERSION,BUILD_REVISION,APP_RELEASE_ID,APP_RELEASE_SEQUENCE},worker:info,snapshot:{themePreference:snap.themePreference,fontLevel:snap.fontLevel,lastHour:snap.lastHour},sentinel:localStorage.getItem('APP_GOV_SENTINEL'),controller:!!navigator.serviceWorker.controller,caches:await caches.keys(),body:(document.body.innerText||'').trim().slice(0,200)};
  });
  out.steps.post=post;
  if(post.identity.APP_RELEASE_ID!=='24h-v120-b5-20261002-blind-adversarial-repair'||post.identity.BUILD_REVISION!=='B5')throw new Error('post_page_identity_wrong');
  if(!post.worker||post.worker.releaseId!==post.identity.APP_RELEASE_ID)throw new Error('post_worker_identity_wrong');
  if(post.snapshot.themePreference!=='dark'||post.snapshot.fontLevel!=='xlarge'||String(post.snapshot.lastHour)!=='3')throw new Error('personal_state_lost_after_update');
  if(post.sentinel!=='24H-B5-UPGRADE')throw new Error('sentinel_lost_after_update');

  await ctx.setOffline(true);
  await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120',null,{timeout:15000});
  const off1=await p.evaluate(()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,sentinel:localStorage.getItem('APP_GOV_SENTINEL'),snap:(()=>{const s=buildPersonalSnapshotFromState();return{themePreference:s.themePreference,fontLevel:s.fontLevel,lastHour:s.lastHour}})(),body:(document.body.innerText||'').trim().slice(0,120)}));
  out.steps.offline1=off1;
  await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120',null,{timeout:15000});
  const off2=await p.evaluate(()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,sentinel:localStorage.getItem('APP_GOV_SENTINEL'),body:(document.body.innerText||'').trim().slice(0,120)}));
  out.steps.offline2=off2;
  if(off1.id!==post.identity.APP_RELEASE_ID||off2.id!==post.identity.APP_RELEASE_ID||off1.sentinel!=='24H-B5-UPGRADE'||off2.sentinel!=='24H-B5-UPGRADE')throw new Error('offline_reopen_identity_or_state_failure');

  await ctx.setOffline(false); await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120');
  out.steps.onlineRecovery=await p.evaluate(async()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,caches:await caches.keys(),controller:!!navigator.serviceWorker.controller}));
  out.consoleErrors=consoleErrors; out.pageErrors=pageErrors;
  if(pageErrors.length)throw new Error('page_errors:'+pageErrors.join('|'));
  fs.writeFileSync('24h-b5-production-upgrade-offline-results.json',JSON.stringify(out,null,2));
  console.log('24H_B5_PRODUCTION_UPGRADE_OFFLINE_PASS');
  await ctx.close(); await browser.close();
})().catch(async e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b5-production-upgrade-offline-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
