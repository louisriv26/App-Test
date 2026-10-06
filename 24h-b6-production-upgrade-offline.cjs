
const {chromium}=require('playwright');
const fs=require('fs'), path=require('path');
function copy(src,dst){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}
const pred='24h-v119-b1-governed-r4', succ='24h-v120-b6-blind-closure', dst=path.join('qa-24h-b6-upgrade','app');
const url='http://127.0.0.1:8086/app/luisa_24_heures.html';
const out={generated_at:new Date().toISOString(),pred,succ,steps:{}};
(async()=>{
  copy(pred,dst);
  const browser=await chromium.launch({headless:true});
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  let p=await ctx.newPage(); const consoleErrors=[],pageErrors=[];
  p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
  p.on('pageerror',e=>pageErrors.push(String(e.message||e)));
  let r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000}); if(!r||!r.ok())throw new Error('predecessor_http');
  await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v119',null,{timeout:30000});
  await p.evaluate(async()=>{await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('v119_ready_timeout')),12000))])});
  await p.reload({waitUntil:'domcontentloaded',timeout:30000});
  await p.waitForFunction(()=>navigator.serviceWorker.controller && typeof APP_VERSION!=='undefined' && APP_VERSION==='v119',null,{timeout:15000});
  await p.evaluate(async()=>{
    localStorage.setItem('APP_GOV_SENTINEL','24H-B6-UPGRADE');
    await setThemePreference('dark');
    await changeFontSize('xlarge');
    openHour(3);
    await new Promise(r=>setTimeout(r,450));
    const ok=await flushAndVerifyPersonalStateForUpdate(4000);
    if(!ok) throw new Error('predecessor_state_flush_failed');
  });
  const pre=await p.evaluate(async()=>{
    const reg=await navigator.serviceWorker.ready;
    const info=await queryWorkerRelease(reg.active);
    const snap=buildPersonalSnapshotFromState();
    return {identity:{APP_VERSION,BUILD_REVISION,APP_RELEASE_ID,APP_RELEASE_SEQUENCE},worker:info,controlled:!!navigator.serviceWorker.controller,controllerScript:navigator.serviceWorker.controller&&navigator.serviceWorker.controller.scriptURL,snapshot:{themePreference:snap.themePreference,fontLevel:snap.fontLevel,lastHour:snap.lastHour},sentinel:localStorage.getItem('APP_GOV_SENTINEL'),caches:await caches.keys()};
  });
  out.steps.pre=pre;
  if(!pre.controlled||pre.identity.APP_VERSION!=='v119'||!pre.worker||pre.worker.version!=='v119')throw new Error('predecessor_not_genuinely_controlled_v119');
  if(pre.snapshot.themePreference!=='dark'||pre.snapshot.fontLevel!=='xlarge'||String(pre.snapshot.lastHour)!=='3')throw new Error('pre_state_not_committed');

  copy(succ,dst);
  const prep=await p.evaluate(async()=>{
    const ok=await checkForUpdate(true,'blind-b6-upgrade');
    await new Promise(r=>setTimeout(r,200));
    const pu=_preparedUpdate;
    return {checkResult:ok,prepared:!!pu,mode:pu&&pu.mode,remote:pu&&pu.remote?{sequence:pu.remote.sequence,version:pu.remote.version,releaseId:pu.remote.releaseId,shellHash:pu.remote.shellHash}:null,worker:pu&&pu.worker?await queryWorkerRelease(pu.worker):null,reg:pu&&pu.registration?{waiting:pu.registration.waiting&&pu.registration.waiting.state,active:pu.registration.active&&pu.registration.active.state}:null,status:document.getElementById('updateCheckStatus')?.textContent||''};
  });
  out.steps.prepared=prep;
  if(!prep.prepared||prep.mode!=='waiting'||!prep.reg||prep.reg.waiting!=='installed')throw new Error('successor_not_waiting_installed');
  if(!prep.worker||prep.worker.releaseId!=='24h-v120-b6-20261002-blind-adversarial-closure'||prep.worker.version!=='v120'||prep.worker.workerState!=='installed')throw new Error('prepared_worker_identity_or_state_wrong');

  const nav=p.waitForURL(u=>u.href.includes('lp_update_tx=')&&u.pathname.endsWith('/luisa_24_heures.html'),{timeout:30000,waitUntil:'domcontentloaded'});
  await p.locator('.update-refresh-btn').click();
  await nav;
  await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120'&&BUILD_REVISION==='B6'&&!!navigator.serviceWorker.controller,null,{timeout:30000});
  await p.waitForTimeout(1000);
  const post=await p.evaluate(async()=>{
    const reg=await navigator.serviceWorker.ready; const info=await queryWorkerRelease(reg.active); const snap=buildPersonalSnapshotFromState();
    const cachesNow=await caches.keys();
    return {identity:{APP_VERSION,BUILD_REVISION,APP_RELEASE_ID,APP_RELEASE_SEQUENCE},worker:info,snapshot:{themePreference:snap.themePreference,fontLevel:snap.fontLevel,lastHour:snap.lastHour},sentinel:localStorage.getItem('APP_GOV_SENTINEL'),controller:!!navigator.serviceWorker.controller,caches:cachesNow,body:(document.body.innerText||'').trim().slice(0,200)};
  });
  out.steps.post=post;
  if(post.identity.APP_RELEASE_ID!=='24h-v120-b6-20261002-blind-adversarial-closure'||post.identity.BUILD_REVISION!=='B6')throw new Error('post_page_identity_wrong');
  if(!post.worker||post.worker.releaseId!==post.identity.APP_RELEASE_ID||post.worker.workerState!=='activated')throw new Error('post_worker_identity_wrong');
  if(post.snapshot.themePreference!=='dark'||post.snapshot.fontLevel!=='xlarge'||String(post.snapshot.lastHour)!=='3')throw new Error('personal_state_lost_after_update');
  if(post.sentinel!=='24H-B6-UPGRADE')throw new Error('sentinel_lost_after_update');
  const appCaches=post.caches.filter(x=>/-v120-b6$/.test(x));
  if(appCaches.length!==1||!/^luisa-24h-[0-9a-f]{8}-v120-b6$/.test(appCaches[0]))throw new Error('post_cache_not_scope_derived');
  const marker='$'+'{CACHE_PREFIX}';
  if(post.caches.some(x=>x.includes(marker)||x.includes('\\'+marker)))throw new Error('literal_cache_prefix_present');

  await ctx.setOffline(true);
  await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120'&&BUILD_REVISION==='B6',null,{timeout:15000});
  const off1=await p.evaluate(()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,sentinel:localStorage.getItem('APP_GOV_SENTINEL'),snap:(()=>{const s=buildPersonalSnapshotFromState();return{themePreference:s.themePreference,fontLevel:s.fontLevel,lastHour:s.lastHour}})(),body:(document.body.innerText||'').trim().slice(0,120)}));
  out.steps.offline1=off1;
  await p.close();
  p=await ctx.newPage();
  p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
  p.on('pageerror',e=>pageErrors.push(String(e.message||e)));
  await p.goto(url,{waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120'&&BUILD_REVISION==='B6',null,{timeout:15000});
  const off2=await p.evaluate(()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,sentinel:localStorage.getItem('APP_GOV_SENTINEL'),snap:(()=>{const s=buildPersonalSnapshotFromState();return{themePreference:s.themePreference,fontLevel:s.fontLevel,lastHour:s.lastHour}})(),body:(document.body.innerText||'').trim().slice(0,120)}));
  out.steps.offline2=off2;
  for(const x of [off1,off2]){
    if(x.id!==post.identity.APP_RELEASE_ID||x.sentinel!=='24H-B6-UPGRADE'||x.snap.themePreference!=='dark'||x.snap.fontLevel!=='xlarge'||String(x.snap.lastHour)!=='3')throw new Error('offline_reopen_identity_or_state_failure');
  }
  await ctx.setOffline(false); await p.reload({waitUntil:'domcontentloaded',timeout:30000}); await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='v120'&&BUILD_REVISION==='B6');
  out.steps.onlineRecovery=await p.evaluate(async()=>({id:APP_RELEASE_ID,build:BUILD_REVISION,caches:await caches.keys(),controller:!!navigator.serviceWorker.controller}));
  out.consoleErrors=consoleErrors; out.pageErrors=pageErrors;
  if(pageErrors.length)throw new Error('page_errors:'+pageErrors.join('|'));
  fs.writeFileSync('24h-b6-production-upgrade-offline-results.json',JSON.stringify(out,null,2));
  console.log('24H_B6_PRODUCTION_UPGRADE_OFFLINE_PASS');
  await ctx.close(); await browser.close();
})().catch(async e=>{out.error=String(e&&e.stack||e);try{fs.writeFileSync('24h-b6-production-upgrade-offline-results.json',JSON.stringify(out,null,2))}catch(_){}console.error(e);process.exit(1)});
