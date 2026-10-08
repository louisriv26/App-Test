import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const ROOT=process.env.LDC_NESTED_FIXTURE_DIR||'',PORTS=[8992,8993],
 EXPECT_ZIP='954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb',
 report={
 schema:'ldc-v14218-exact-zip-nested-two-origin-adversarial-browser-v1',
 candidate_zip_sha256:EXPECT_ZIP,candidate_source_commit:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 tested_at:new Date().toISOString(),status:'NOT_RUN',checks:{},measurements:{},errors:[],
 limits:['Ephemeral localhost:8992 vs :8993 only; NOT hosted E16/E19 closure','Chromium emulated viewport only; NOT physical iPhone/iPad Safari','No GitHub Pages or production origin visited','No permission to deploy'],
 hosted_e16:'OPEN',hosted_e19:'OPEN',physical_gate:'OPEN',deploy_authority:'NONE'};
const check=(n,ok,info)=>{report.checks[n]=!!ok;if(info!==undefined)report.measurements[n]=info};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let browser,servers=[];
try{
 if(!ROOT||!fs.existsSync(ROOT+'/ldc/PACKAGE_MANIFEST_SHA256.json'))throw Error('NESTED_EXACT_ARCHIVE_FIXTURE_MISSING');
 const manifest=JSON.parse(fs.readFileSync(ROOT+'/ldc/PACKAGE_MANIFEST_SHA256.json','utf8'));
 check('fixture_uses_exact_frozen_package_identity',manifest.source_commit===report.candidate_source_commit&&manifest.app_test_authority==='NONE'&&manifest.files.length===273,manifest.source_commit);
 for(const p of PORTS)servers.push(cp.spawn('python3',['-m','http.server',String(p),'--bind','127.0.0.1','--directory',ROOT],{stdio:['ignore','ignore','inherit']}));
 await sleep(950);
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'});
 const A='http://127.0.0.1:'+PORTS[0]+'/',B='http://127.0.0.1:'+PORTS[1]+'/';
 const a=await context.newPage(),b=await context.newPage(),root=await context.newPage(),sib=await context.newPage();
 for (const [page,url] of [[root,A],[sib,A+'24h/']])await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
 const rootState=await root.evaluate(async()=>({controller:!!navigator.serviceWorker.controller,regs:(await navigator.serviceWorker.getRegistrations()).map(x=>x.scope),hasIndexedDB:document.documentElement.innerHTML.includes('indexedDB.open')}));
 check('neutral_root_not_a_PWA_and_no_DB',!rootState.controller&&!rootState.regs.length&&!rootState.hasIndexedDB,rootState);
 const siblingBefore=await sib.evaluate(()=>({controller:!!navigator.serviceWorker.controller,title:document.title}));
 check('sibling_before_LDC_has_no_worker',!siblingBefore.controller,siblingBefore);
 const pageErrors=[];
 for(const pg of [a,b]){pg.on('pageerror',err=>pageErrors.push(String(err)));pg.setDefaultTimeout(180000)}
 async function boot(page,origin){
  await page.goto(origin+'ldc/',{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
  await page.evaluate(()=>{if(document.getElementById('onboarding-overlay')&&getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
  await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;if(!r.active)throw Error('NO_ACTIVE_SW')});
  return page.evaluate(async()=>({version:PUBLIC_VERSION,db:DB_NAME,scope:(await navigator.serviceWorker.getRegistrations()).map(r=>r.scope),
   controller:!!navigator.serviceWorker.controller,cacheKeys:await caches.keys(),
   semanticLazy:LDCPLSV16Runtime.status().ready===false}));
 }
 const av=await boot(a,A);
 const bv=await boot(b,B);
 check('nested_LDC_both_ports_boot_exact_version',av.version==='142.18'&&bv.version==='142.18'&&av.db==='ldc_user_v1'&&bv.db==='ldc_user_v1',{a:av,b:bv});
 check('worker_scopes_strictly_app_folder_both_origins',av.scope.length===1&&av.scope[0]===A+'ldc/'&&bv.scope.length===1&&bv.scope[0]===B+'ldc/',{a:av.scope,b:bv.scope});
 check('semantic_model_lazy_at_nested_boot',av.semanticLazy&&bv.semanticLazy,{a:av.semanticLazy,b:bv.semanticLazy});
 await sib.reload({waitUntil:'domcontentloaded'});
 check('nested_worker_never_controls_sibling_24h',await sib.evaluate(()=>!navigator.serviceWorker.controller));
 await root.reload({waitUntil:'domcontentloaded'});
 check('nested_worker_never_controls_neutral_root',await root.evaluate(()=>!navigator.serviceWorker.controller));
 await a.evaluate(async()=>{await dbPut('settings',{key:'__r7_origin_probe',val:'ORIGIN_A_R7'});localStorage.setItem('__r7_origin_probe','A');(await caches.open('__r7_origin_probe_A')).put('./marker',new Response('A'))});
 const b0=await b.evaluate(async()=>({db:await dbGet('settings','__r7_origin_probe'),local:localStorage.getItem('__r7_origin_probe'),caches:await caches.keys()}));
 check('origin_A_cannot_modify_B_db_or_local_or_cache',b0.db==null&&b0.local==null&&!b0.caches.includes('__r7_origin_probe_A'),b0);
 await b.evaluate(async()=>{await dbPut('settings',{key:'__r7_origin_probe',val:'ORIGIN_B_R7'});localStorage.setItem('__r7_origin_probe','B');await (await caches.open('__r7_origin_probe_B')).put('./marker',new Response('B'))});
 const a0=await a.evaluate(async()=>({db:await dbGet('settings','__r7_origin_probe'),local:localStorage.getItem('__r7_origin_probe'),caches:await caches.keys()}));
 check('origin_B_cannot_modify_A_db_or_local_or_cache',a0.db?.val==='ORIGIN_A_R7'&&a0.local==='A'&&!a0.caches.includes('__r7_origin_probe_B'),a0);
 const query="Deuxième, il ne faut pas regarder le passé. Le passé est passé et il faut vivre dans le présent. Ce n'est pas utile du tout de regarder dans le passé. C'est un affront à Jésus. C'est le deuxième texte.";
 await a.evaluate(async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},query);
 await a.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
 const res=await a.evaluate(()=>({top:searchLastPayload?.payload?.results?.[0]?.entry_id,model:LDCPLSV16Runtime.status().ready,count:document.querySelectorAll('#search-results .result-card').length}));
 check('nested_exact_zip_semantic_real_search',res.top==='ldc_t09_1909_11_02_e001'&&res.model===true&&res.count===20,res);
 await a.locator('#search-results .result-card').first().click();
 await a.waitForFunction(()=>document.querySelector('#screen-reader')?.classList.contains('active'),null,{timeout:60000});
 const landscapeBefore=await a.evaluate(()=>({entry:currentEntry?.id,body:document.getElementById('reader-body')?.innerText?.trim().length||0,scroll:document.getElementById('reader-scroll')?.clientHeight||0}));
 await a.setViewportSize({width:844,height:390});
 await sleep(1250);
 const landscapeAfter=await a.evaluate(()=>({entry:currentEntry?.id,body:document.getElementById('reader-body')?.innerText?.trim().length||0,scroll:document.getElementById('reader-scroll')?.clientHeight||0,visible:document.querySelector('#screen-reader')?.classList.contains('active')}));
 check('nested_reader_portrait_landscape_no_blank',landscapeBefore.body>100&&landscapeAfter.body>100&&landscapeAfter.visible&&landscapeAfter.scroll>45&&landscapeAfter.entry===res.top,{portrait:landscapeBefore,landscape:landscapeAfter});
 await a.setViewportSize({width:390,height:844});
 await a.locator('#reader-back-btn').click();
 await a.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active'),null,{timeout:60000});
 const retImmediately=await a.evaluate(()=>({count:document.querySelectorAll('#search-results .result-card').length,searchBusy:!!searchBusyGeneration}));
 try{await a.waitForFunction(()=>document.querySelectorAll('#search-results .result-card').length===20,null,{timeout:20000,polling:100})}catch(_){}
 const retFinal=await a.evaluate(()=>({count:document.querySelectorAll('#search-results .result-card').length,screen:document.querySelector('.screen.active')?.id,query:searchQueryDraftCanonical(),searchBusy:!!searchBusyGeneration}));
 check('nested_reader_return_retains_20_results',retFinal.count===20&&retFinal.screen==='screen-search'&&retFinal.query===query,{immediate:retImmediately,afterAsyncReentry:retFinal});
 const offlineBefore=await a.evaluate(async()=>await requestOfflineStatus());
 check('nested_sw_reports_exact_offline_asset_count',offlineBefore.total===204,{state:offlineBefore.state,total:offlineBefore.total});
 await a.evaluate(async()=>await startOfflinePreparation());
 await a.waitForFunction(()=>['READY','ERROR','PARTIAL'].includes(offlineUiState.state),null,{timeout:20*60*1000,polling:500});
 const ready=await a.evaluate(async()=>await requestOfflineStatus());
 check('nested_exact_zip_all_204_offline_assets_cached',ready.state==='READY'&&ready.completed===204&&ready.total===204,{state:ready.state,completed:ready.completed,total:ready.total,failed:ready.failed});
 await context.setOffline(true);
 await a.reload({waitUntil:'domcontentloaded',timeout:90000});
 await a.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:90000});
 const off=await a.evaluate(async()=>{
  const r=await requestOfflineStatus();const counts=[];
  for(const vol of [1,18,36]){await ensureVolumeReaderData(vol);counts.push({vol,count:corpusCache[vol]?.entries?.length||0})}
  return {state:r.state,total:r.total,completed:r.completed,counts};
 });
 check('nested_offline_fresh_reload_and_3_tomes',off.state==='READY'&&off.completed===204&&off.counts.length===3&&off.counts.every(x=>x.count>0),off);
 // Test cold offline semantic error as an explicit fail-safe, not as a promised offline feature.
 // Do not mistake Playwright offline emulation for a proven outage of Service Worker network fetches:
 // shut down port B's actual server before reloading, to prohibit every origin-B network fallback.
 const bBeforeHardOffline=await b.evaluate(()=>({ready:LDCPLSV16Runtime.status().ready,cacheNames:[],busy:!!searchBusyGeneration}));
 servers[1].kill('SIGTERM');await new Promise(resolve=>servers[1].once('exit',resolve));
 await b.reload({waitUntil:'domcontentloaded',timeout:90000});
 await b.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:90000});
 const bBeforeColdQuery=await b.evaluate(()=>({ready:LDCPLSV16Runtime.status().ready,canInitialize:LDCPLSV16Runtime.status().can_initialize}));
 await b.evaluate(async()=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft('Jésus appelle notre volonté à vivre dans la Divine Volonté',{mode:'meaning',syncOther:true});await runSearch()});
 await b.waitForFunction(()=>!searchBusyGeneration,null,{timeout:120000});
 const offlineSemantic=await b.evaluate(()=>({busy:!!searchBusyGeneration,heading:document.getElementById('search-meta')?.innerText?.slice(0,250)||'',
  cards:document.querySelectorAll('#search-results .result-card').length,notice:document.getElementById('search-results')?.innerText?.slice(0,500)||'',ready:LDCPLSV16Runtime.status().ready}));
 check('offline_uncached_semantic_fails_closed_without_spinner',
  !bBeforeColdQuery.ready&&!offlineSemantic.busy&&offlineSemantic.cards===0&&!offlineSemantic.ready&&
  /(indisponible|impossible|connexion|hors ligne|pas pu|erreur|non encore qualifié)/i.test(offlineSemantic.heading+' '+offlineSemantic.notice),
  {beforeOfflineMode:bBeforeHardOffline,beforeColdQuery:bBeforeColdQuery,afterAttempt:offlineSemantic,serverBTerminated:true});
 check('no_unhandled_pageerrors',!pageErrors.length,pageErrors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS_EXACT_ARCHIVE_NESTED_TWO_ORIGINS_LOCAL_ONLY':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e))}
finally{
 fs.writeFileSync('LDC_v142.18_EXACT_ZIP_NESTED_ORIGIN_OFFLINE_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 for(const p of servers)p.kill('SIGTERM');
 if(report.status!=='PASS_EXACT_ARCHIVE_NESTED_TWO_ORIGINS_LOCAL_ONLY')process.exitCode=1;
}
