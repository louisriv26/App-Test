const { chromium, webkit } = require('playwright');
const fs=require('fs'), path=require('path'), cp=require('child_process');
const REMOTE='https://louisriv26.github.io/App-Test/';
const LOCAL='http://127.0.0.1:8215/';
const UPGRADE='http://127.0.0.1:8216/';
const EXPECT_APP='v2.19.142.15-R1B-RELEASE-TRUTH-SCOPE-CLOSURE';
const EXPECT_PUB='142.15';
const EXPECT_SW='ldc-v2.19.142.15-R1B-release-truth-scope-closure';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const out={generated_at:new Date().toISOString(),candidate:EXPECT_APP,remote:{},local:{},upgrade:{},webkit:{},findings:[],errors:[]};
function fail(scope,msg,detail){out.errors.push({scope,msg,detail});}
async function ready(p,timeout=120000){
  await p.waitForFunction(()=>{const l=document.getElementById('loading'),v=document.getElementById('version-pill-home');return l&&getComputedStyle(l).display==='none'&&v&&v.textContent&&!/v—|v-$/.test(v.textContent);},{timeout});
  await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none'&&typeof finishOnboarding==='function')finishOnboarding();});
  await sleep(300);
}
async function ensureController(p){
  const a=await p.evaluate(async()=>{if(!('serviceWorker'in navigator))return {supported:false};const r=await navigator.serviceWorker.ready;return {supported:true,active:!!r.active,controller:!!navigator.serviceWorker.controller,scope:r.scope,script:r.active&&r.active.scriptURL};});
  if(a.supported&&a.active&&!a.controller){await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p);return p.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return {supported:true,active:!!r.active,controller:!!navigator.serviceWorker.controller,scope:r.scope,script:r.active&&r.active.scriptURL};});}
  return a;
}
async function identity(p){
  return p.evaluate(()=>({app:APP_VERSION,pub:PUBLIC_VERSION,sw:SW_CACHE_VERSION,label:APP_VERSION_LABEL,screen:document.querySelector('.screen.active')?.id||null,versionPill:document.getElementById('version-pill-home')?.textContent||''}));
}
async function e07matrix(p){
  return p.evaluate(async()=>{
    const rows=[];
    for(const view of ['enriched','aflp','additions']){
      await setSupplementMode(view,{persist:false,rerender:false,silent:true,origin:'qa'});
      for(const mode of ['words','meaning']){
        setSearchIntentMode(mode,{rerun:false,persist:false});
        renderSearchIntentMode();
        const n=document.getElementById('search-semantic-scope-note');
        rows.push({view,mode,hidden:n.hidden,text:n.textContent});
      }
    }
    await setSupplementMode('enriched',{persist:false,rerender:false,silent:true,origin:'qa'});
    setSearchIntentMode('words',{rerun:false,persist:false});
    return rows;
  });
}
async function lexical(p,q='Fiat',mode='enriched'){
  await p.evaluate(async({q,mode})=>{await goSearch();await setSupplementMode(mode,{persist:false,rerender:false,silent:true,origin:'qa'});setSearchIntentMode('words',{rerun:false,persist:false});const i=document.getElementById('search-input');i.value=q;onSearchInput('words');await runSearch();},{q,mode});
  await p.waitForFunction(()=>document.querySelectorAll('#search-results .result-card').length>0,{timeout:120000});
  return p.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,meta:document.getElementById('search-meta')?.textContent||'',first:document.querySelector('#search-results .result-card')?.dataset.resultKey||null,mode:supplementMode,payload:searchLastPayload&&{semantic:!!searchLastPayload.semantic,total:searchLastPayload.foundation?.totalMatches||searchLastPayload.total||null}}));
}
async function semantic(p,q){
  const t=Date.now();
  await p.evaluate(async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});const i=document.getElementById('search-input-meaning');i.value=q;onSearchInput('meaning');await runSearch();},q);
  await p.waitForFunction(()=>document.getElementById('search-progress')?.textContent===''||getComputedStyle(document.getElementById('search-progress')).display==='none',{timeout:360000}).catch(()=>{});
  await p.waitForTimeout(500);
  return p.evaluate(ms=>({elapsed_ms:Date.now()-ms,cards:document.querySelectorAll('#search-results .result-card').length,meta:document.getElementById('search-meta')?.textContent||'',text:document.getElementById('search-results')?.innerText.slice(0,600)||'',confidence:searchLastPayload?.payload?.confidence||searchLastPayload?.confidence||null}),t);
}
async function firstEntryJourney(p){
  await p.evaluate(()=>goTomes());
  await p.waitForFunction(()=>document.querySelectorAll('#tomes-list .vol-card').length===36,{timeout:90000});
  const tomes=await p.locator('#tomes-list .vol-card').count();
  await p.locator('#tomes-list .vol-card').first().click();
  await p.waitForFunction(()=>document.getElementById('screen-entries')?.classList.contains('active')&&document.querySelector('#entries-list .entry-item'),{timeout:90000});
  const entryId=await p.locator('#entries-list .entry-item').first().getAttribute('data-entry-id');
  await p.locator('#entries-list .entry-item').first().click();
  await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active')&&document.querySelectorAll('#reader-body .para-fragment').length>0,{timeout:90000});
  const reader=await p.evaluate(()=>({vol:currentVolume,entry:currentEntry&&currentEntry.id,paras:document.querySelectorAll('#reader-body .para-fragment').length,scrollHeight:document.getElementById('reader-scroll').scrollHeight,clientHeight:document.getElementById('reader-scroll').clientHeight}));
  return {tomes,entryId,reader};
}
async function userState(p,entryId){
  const favBefore=await p.getAttribute('#reader-fav-top','aria-pressed');
  await p.click('#reader-fav-top'); await sleep(250);
  const fav=await p.evaluate(id=>dbGet('favorites',id),entryId);
  const note=await p.evaluate(async()=>{
    const para=document.querySelector('#reader-body .para-fragment');
    if(!para)return {saved:false,reason:'no para'};
    const pid=para.dataset.paraId;
    if(!pid)return {saved:false,reason:'no para id'};
    showParagraphContext(pid);
    contextNote();
    document.getElementById('note-input').value='QA v142.15 note sentinel';
    await saveNote();
    const all=await dbGetAll('notes');
    return {saved:all.some(x=>x.text==='QA v142.15 note sentinel'),count:all.length,para_id:pid};
  });
  const pos=await p.evaluate(async()=>{
    const sc=document.getElementById('reader-scroll');sc.scrollTop=Math.min(700,Math.max(0,sc.scrollHeight-sc.clientHeight));onReaderScroll();await new Promise(r=>setTimeout(r,900));if(typeof flushActiveReaderSession==='function')await flushActiveReaderSession({invalidate:false}).catch(()=>{});const rows=await dbGetAll('reading_pos');return {count:rows.length,main:rows.find(x=>x.key==='main')||null,scrollTop:sc.scrollTop};
  });
  const backup=await p.evaluate(async()=>{const b=await buildUserDataStreamBackup();return {records:b.totalRecords,crc32:b.crc32,parts:b.parts.length,counts:b.counts};});
  return {favBefore,favStored:!!fav,note,pos,backup};
}
async function reopenState(p,entryId){
  await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p);
  const db=await p.evaluate(async id=>({fav:!!(await dbGet('favorites',id)),note:(await dbGetAll('notes')).some(x=>x.text==='QA v142.15 note sentinel'),reading:(await dbGetAll('reading_pos')).length,mode:supplementMode}),entryId);
  await p.evaluate(()=>goTomes());await p.waitForFunction(()=>document.querySelectorAll('#tomes-list .vol-card').length===36,{timeout:90000});await p.locator('#tomes-list .vol-card').first().click();await p.waitForFunction(()=>document.querySelector('#entries-list .entry-item'),{timeout:90000});
  await p.locator('#entries-list .entry-item').first().click();await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),{timeout:90000});
  const aria=await p.getAttribute('#reader-fav-top','aria-pressed');
  await p.click('#reader-fav-top'); // cleanup favourite
  return {...db,favAria:aria};
}
async function searchReturn(p){
  const s=await lexical(p,'volonté divine','enriched');
  const cards=p.locator('#search-results .result-card');const n=await cards.count();const idx=Math.min(6,n-1);const card=cards.nth(idx);const key=await card.getAttribute('data-result-key');
  await card.scrollIntoViewIfNeeded();const before=await card.boundingBox();await card.click();
  await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),{timeout:90000});
  await p.evaluate(()=>backFromReader());
  await p.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active')&&document.querySelectorAll('#search-results .result-card').length>0,{timeout:90000});await sleep(400);
  const after=await p.locator('#search-results .result-card').filter({has:p.locator('xpath=.')}).count().catch(()=>0);
  const present=await p.evaluate(k=>[...document.querySelectorAll('#search-results .result-card')].some(x=>x.dataset.resultKey===k),key);
  return {initial:s,key,present,countAfter:after,beforeTop:before&&before.y};
}
async function hostedChromium(){
  const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:390,height:844},serviceWorkers:'allow',locale:'fr-FR'});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push('page:'+e));p.on('console',m=>{if(m.type()==='error')errs.push('console:'+m.text())});
  try{
    const r=await p.goto(REMOTE+'?qa='+Date.now(),{waitUntil:'domcontentloaded',timeout:120000});await ready(p);
    out.remote.http_status=r&&r.status();out.remote.identity=await identity(p);out.remote.sw=await ensureController(p);
    out.remote.e15=await p.evaluate(()=>({old:(document.documentElement.textContent.match(/qualifié séparément/g)||[]).length,newText:(document.documentElement.textContent.match(/que la campagne de correction textuelle décrite ici ne couvre pas/g)||[]).length}));
    out.remote.e07=await e07matrix(p);
    out.remote.journey=await firstEntryJourney(p);out.remote.user_state=await userState(p,out.remote.journey.entryId);out.remote.reopen=await reopenState(p,out.remote.journey.entryId);
    out.remote.search=await searchReturn(p);
    await p.evaluate(async()=>{await goSearch();await setSupplementMode('aflp',{persist:false,rerender:false,silent:true,origin:'qa'});setSearchIntentMode('meaning',{rerun:false,persist:false});renderSearchIntentMode();});
    out.remote.e07_live=await p.evaluate(()=>({hidden:document.getElementById('search-semantic-scope-note').hidden,text:document.getElementById('search-semantic-scope-note').textContent}));
    out.remote.semantic_natural=await semantic(p,"Je me souviens d'un passage où Jésus parle de vivre dans la Divine Volonté et de laisser sa volonté humaine.");
    out.remote.semantic_noise=await semantic(p,'pizza quantique banane zzqxk 8472');
    out.remote.layout=await p.evaluate(()=>{applyTextLevel('xlarge');const n=document.getElementById('search-semantic-scope-note'),sc=document.getElementById('search-scroll');return {innerWidth,scrollWidth:document.documentElement.scrollWidth,noteRect:n.getBoundingClientRect().toJSON(),searchClient:sc.clientHeight,searchScroll:sc.scrollHeight};});
    out.remote.errors=errs;
  }catch(e){fail('remote',String(e&&e.stack||e));}
  await c.close();await b.close();
}
async function localOffline(){
  const profile=path.join(process.cwd(),'.qa14215-offline-profile');fs.rmSync(profile,{recursive:true,force:true});
  let c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});let p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  try{
    await p.goto(LOCAL,{waitUntil:'domcontentloaded',timeout:120000});await ready(p);await ensureController(p);
    await p.evaluate(()=>startOfflinePreparation());
    await p.waitForFunction(()=>['READY','ERROR','PARTIAL'].includes(offlineUiState.state),{timeout:360000});
    out.local.offline_prepare=await p.evaluate(()=>({state:offlineUiState.state,completed:offlineUiState.completed,total:offlineUiState.total,failed:offlineUiState.failed?.length||0,total_bytes:offlineUiState.total_bytes,caches:null}));
    out.local.offline_prepare.caches=await p.evaluate(()=>caches.keys());
    await c.setOffline(true);await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p);
    const nav=await p.evaluate(async()=>{await goTomes();await openTome(30);return {screen:document.querySelector('.screen.active')?.id,entries:document.querySelectorAll('#entries-list .entry-item').length,app:APP_VERSION};});
    const lex=await lexical(p,'Fiat','enriched');
    out.local.offline_warm={nav,lex};
    await c.close();
    c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});await c.setOffline(true);p=await c.newPage();let navok=true,naverr=null;try{await p.goto(LOCAL,{waitUntil:'domcontentloaded',timeout:90000});await ready(p);}catch(e){navok=false;naverr=String(e)}
    out.local.offline_cold={navok,naverr,identity:navok?await identity(p):null,body:navok?(await p.locator('body').innerText()).slice(0,200):null};
  }catch(e){fail('localOffline',String(e&&e.stack||e));}
  await c.close();out.local.errors=errs;
}
async function webkitCore(){
  let b;try{b=await webkit.launch({headless:true});const c=await b.newContext({viewport:{width:390,height:844},locale:'fr-FR'});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));const r=await p.goto(REMOTE+'?webkitqa='+Date.now(),{waitUntil:'domcontentloaded',timeout:120000});await ready(p);out.webkit.http_status=r&&r.status();out.webkit.identity=await identity(p);out.webkit.e07=await e07matrix(p);out.webkit.lexical=await lexical(p,'Fiat','enriched');out.webkit.journey=await firstEntryJourney(p);out.webkit.errors=errs;await c.close();}catch(e){out.webkit.error=String(e&&e.stack||e)}finally{if(b)await b.close();}
}
function staticServer(){
  const script=path.join(process.cwd(),'.github/qa-v14215-full/switch-server.cjs');
  const child=cp.spawn(process.execPath,[script],{stdio:['ignore','ignore','inherit'],env:{...process.env,PORT:'8216',ACTIVE_FILE:'/tmp/ldc14215_active_root'}});
  return child;
}
async function upgrade(){
  try{
    const old='/tmp/ldc14210-tree',cur='/tmp/ldc14215-tree';fs.rmSync(old,{recursive:true,force:true});fs.rmSync(cur,{recursive:true,force:true});fs.mkdirSync(old,{recursive:true});fs.mkdirSync(cur,{recursive:true});
    cp.execFileSync('bash',['-lc',`git archive 26cee192904e489a9a2be75874208dea150e573f | tar -x -C ${old}`],{stdio:'inherit'});
    cp.execFileSync('bash',['-lc',`git archive 572d9df7927765b575a76eaee98fd3cc9d455e74 | tar -x -C ${cur}`],{stdio:'inherit'});
    fs.writeFileSync('/tmp/ldc14215_active_root',old);
    const server=staticServer();await sleep(1500);
    const profile=path.join(process.cwd(),'.qa14215-upgrade-profile');fs.rmSync(profile,{recursive:true,force:true});
    const c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});const p=await c.newPage();
    await p.goto(UPGRADE,{waitUntil:'domcontentloaded',timeout:120000});await ready(p);await ensureController(p);
    const pre=await identity(p);
    await p.evaluate(async()=>{localStorage.setItem('qa14215-upgrade','keep');await dbPut('settings',{key:'qa14215_upgrade',val:'keep',ts:Date.now()});});
    fs.writeFileSync('/tmp/ldc14215_active_root',cur);await sleep(200);
    const activation=await p.evaluate(async()=>{const reg=await navigator.serviceWorker.getRegistration();let changes=0;navigator.serviceWorker.addEventListener('controllerchange',()=>changes++);await reg.update();let end=Date.now()+45000;while(Date.now()<end&&!reg.waiting){await new Promise(r=>setTimeout(r,250));}if(reg.waiting)reg.waiting.postMessage({type:'SKIP_WAITING'});end=Date.now()+45000;while(Date.now()<end&&changes===0)await new Promise(r=>setTimeout(r,250));return {changes,waiting:!!reg.waiting};});
    await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p);const post=await p.evaluate(async()=>({app:APP_VERSION,pub:PUBLIC_VERSION,local:localStorage.getItem('qa14215-upgrade'),idb:(await dbGet('settings','qa14215_upgrade'))?.val||null,caches:(await caches.keys()).filter(x=>x.startsWith('ldc-le-livre-du-ciel-')).sort()}));const lex=await lexical(p,'Fiat','enriched');
    out.upgrade={pre,activation,post,lex};await c.close();server.kill();
  }catch(e){fail('upgrade',String(e&&e.stack||e));}
}
(async()=>{
  await hostedChromium();
  await localOffline();
  await upgrade();
  await webkitCore();
  const e07ok=out.remote.e07&&out.remote.e07.every(x=>x.hidden===!(x.mode==='meaning'&&(x.view==='aflp'||x.view==='additions')));
  const critical={
    remote_identity:out.remote.identity?.app===EXPECT_APP&&out.remote.identity?.pub===EXPECT_PUB&&out.remote.identity?.sw===EXPECT_SW,
    remote_sw:!!out.remote.sw?.active&&!!out.remote.sw?.controller,
    e15:out.remote.e15?.old===0&&out.remote.e15?.newText===1,
    e07:e07ok&&out.remote.e07_live?.hidden===false,
    navigation:out.remote.journey?.tomes===36&&out.remote.journey?.reader?.paras>0,
    persistence:out.remote.user_state?.favStored&&out.remote.user_state?.note?.saved&&out.remote.reopen?.fav&&out.remote.reopen?.note&&out.remote.reopen?.favAria==='true',
    backup:(out.remote.user_state?.backup?.records||0)>0,
    lexical:(out.remote.search?.initial?.cards||0)>0&&out.remote.search?.present,
    semantic:(out.remote.semantic_natural?.cards||0)>0,
    offline:out.local.offline_prepare?.state==='READY'&&out.local.offline_warm?.nav?.entries>0&&(out.local.offline_warm?.lex?.cards||0)>0&&out.local.offline_cold?.navok,
    upgrade:out.upgrade?.pre?.app==='v2.19.142.10-R1B-PLS-RESULTS-UX-CLOSURE'&&out.upgrade?.post?.app===EXPECT_APP&&out.upgrade?.post?.local==='keep'&&out.upgrade?.post?.idb==='keep'&&out.upgrade?.activation?.changes>=1&&(out.upgrade?.lex?.cards||0)>0,
    webkit:out.webkit?.identity?.app===EXPECT_APP&&(out.webkit?.lexical?.cards||0)>0&&out.webkit?.journey?.reader?.paras>0
  };
  out.critical=critical;
  if((out.remote.semantic_noise?.cards||0)>0)out.findings.push({id:'E04_REPRODUCED',severity:'material-search-quality',detail:'Out-of-domain/gibberish semantic query still returns normal-looking results',cards:out.remote.semantic_noise.cards,confidence:out.remote.semantic_noise.confidence});
  out.overall=Object.values(critical).every(Boolean)?'PASS_TESTED_SCOPE':'FAIL';
  fs.writeFileSync('qa-v14215-full-runtime-results.json',JSON.stringify(out,null,2)+'\n');
  console.log(JSON.stringify(out,null,2));
  if(out.overall==='FAIL')process.exitCode=1;
})().catch(e=>{out.overall='HARNESS_ERROR';out.fatal=String(e&&e.stack||e);fs.writeFileSync('qa-v14215-full-runtime-results.json',JSON.stringify(out,null,2)+'\n');console.error(e);process.exitCode=2;});
