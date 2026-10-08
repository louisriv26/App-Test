import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright-core';
const ROOT='https://louisriv26.github.io/mauritius-mass-finder-beta/';
const APP=ROOT+'ldc/';
const SOURCE='7c292d6221bb350fac3aeaa83750b8784706d45c';
const report={schema:'ldc-v14218-r13-hosted-massfinderbeta-real-https-adversarial-v1',
 tested_at:new Date().toISOString(),origin:new URL(APP).origin,root:ROOT,application_url:APP,
 status:'NOT_RUN',checks:{},details:{},errors:[],warnings:[],
 scope:'Live GitHub Pages remote HTTP + real Chromium automation on fresh ephemeral CI browser context; no owner Safari/device data touched',
 constraints:['Not physical iPhone/iPad','Fresh browser profile cannot detect old Safari root-scope worker leftovers','No main/App-Test/prod deployment mutation','No capacity/real crash simulation','GitHub Pages URL content not automatically proof of a prior iPhone installation'],
 public_release_authority:'NONE'};
const ck=(n,p,d)=>{report.checks[n]=!!p;if(d!==undefined)report.details[n]=d};
const sha=v=>createHash('sha256').update(v).digest('hex');
async function get(url,timeoutMs=110000){
 const c=new AbortController(),timer=setTimeout(()=>c.abort(),timeoutMs);
 try{let r=await fetch(url,{redirect:'follow',signal:c.signal,headers:{'cache-control':'no-cache'}});
 const data=Buffer.from(await r.arrayBuffer());
 return {status:r.status,ok:r.ok,url:r.url,contentType:r.headers.get('content-type'),data};
 }finally{clearTimeout(timer)}
}
let browser,context;
try{
 const [root,app,sw,version,mf]=await Promise.all([
  get(ROOT),get(APP),get(APP+'sw.js'),get(APP+'version.json'),get(APP+'PACKAGE_MANIFEST_SHA256.json')]);
 ck('hosted_root_and_app_and_worker_and_manifest_http_200',[root,app,sw,version,mf].every(x=>x.ok),
  [root,app,sw,version,mf].map(x=>({status:x.status,url:x.url,bytes:x.data.length,type:x.contentType})));
 if(![root,app,sw,version,mf].every(x=>x.ok))throw Error('HOSTED_REQUIRED_RESOURCES_MISSING');
 const manifest=JSON.parse(mf.data.toString('utf8')),v=JSON.parse(version.data.toString('utf8'));
 ck('hosted_application_source_and_version_identical_frozen_R12',manifest.source_commit===SOURCE&&manifest.files?.length===273&&manifest.public_version==='142.18'&&v.app_version.includes('142.18'),{
 manifestSource:manifest.source_commit,manifestFiles:manifest.files?.length,manifestVersion:manifest.public_version,versionJson:v.app_version});
 ck('hosted_worker_version_matches_app',sw.data.toString('utf8').includes('v2.19.142.18-R1B-reader-semantic-integration-wip'),{workerStart:sw.data.toString('utf8').slice(0,95)});
 const rootText=root.data.toString('utf8');
 ck('neutral_root_is_launcher_to_ldc',rootText.includes('href="./ldc/"')&&!rootText.includes('serviceWorker.register')&&!rootText.includes('indexedDB.open'),{
 title:rootText.match(/<title>(.*?)<\/title>/)?.[1],snippet:rootText.slice(-280)});
 const remoteOrigin=new URL(APP).origin,productionOrigin=new URL('https://louisriv26.github.io/Le-livre-du-Ciel---Github/').origin;
 report.details.e19_same_browser_origin={remoteOrigin,productionOrigin,isSame:remoteOrigin===productionOrigin,rootClaimsDistinct:rootText.includes('origine web distincte')};
 report.warnings.push('E19: MassFinder Beta and LDC production are still the same browser origin. Different repo paths do not isolate regular Safari IndexedDB.');
 if(rootText.includes('origine web distincte'))report.warnings.push('R12 launcher says different web origin, which is false when hosted on louisriv26.github.io.');
 const manifestSha=sha(mf.data);
 report.details.hosted_manifest_sha256=manifestSha;
 // Actual remotely served file, not repository blob, must match ALL exact SHA-256 and byte counts.
 let pos=0,done=0;const missing=[],bad=[],httpStatusCounts={},sizes={};
 async function verifyFile(item){
  const path=item.path;
  try{const v=await get(APP+path,110000);
   httpStatusCounts[v.status]=(httpStatusCounts[v.status]||0)+1;
   if(!v.ok){missing.push({path,status:v.status});return}
   const digest=sha(v.data),ok=digest===item.sha256&&v.data.length===item.bytes;
   if(!ok)bad.push({path,expected_bytes:item.bytes,actual_bytes:v.data.length,expected_sha:item.sha256,actual_sha:digest});
   done++;sizes.total=(sizes.total||0)+v.data.length;
  }catch(e){missing.push({path,error:String(e).slice(0,150)})}
 }
 async function worker(){while(pos<manifest.files.length){const item=manifest.files[pos++];await verifyFile(item)}}
 await Promise.all(Array.from({length:12},worker));
 ck('hosted_ALL_273_executable_resources_exact_bytes_sha256',done===273&&bad.length===0&&missing.length===0,{
 count_exact:done,bytes_hashed:sizes.total||0,errors:missing.slice(0,15),digest_mismatches:bad.slice(0,15),httpStatusCounts});
 if(done!==273||bad.length||missing.length){report.warnings.push('One or more remote bytes differ from the frozen package. Do not promote this hosted candidate.')}
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'});
 const pg=await context.newPage(),rootpg=await context.newPage(),errors=[],requestFailures=[];
 pg.on('pageerror',e=>errors.push(String(e)));
 pg.on('requestfailed',r=>requestFailures.push({url:r.url().slice(0,220),failure:r.failure()}));
 pg.setDefaultTimeout(190000);
 await rootpg.goto(ROOT,{waitUntil:'domcontentloaded',timeout:80000});
 const launch=await rootpg.locator('a[href="./ldc/"]').count();
 ck('hosted_root_launcher_link_present',launch===1,{links:launch});
 await pg.goto(APP,{waitUntil:'domcontentloaded',timeout:90000});
 await pg.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 await pg.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
 const boot=await pg.evaluate(async()=>{
  await navigator.serviceWorker.ready;
  const regs=(await navigator.serviceWorker.getRegistrations()).map(x=>({scope:x.scope,script:x.active?.scriptURL}));
  const s={version:PUBLIC_VERSION,app:APP_VERSION,db:DB_NAME,dbver:DB_VER,registrations:regs,
   controller:navigator.serviceWorker.controller?.scriptURL||null,
   semanticReady:typeof LDCPLSV16Runtime!=='undefined'&&LDCPLSV16Runtime.status().ready,
   manifestUrl:new URL(document.querySelector('link[rel="manifest"]').getAttribute('href'),location.href).href};
  return s;
 });
 ck('hosted_fresh_Chromium_application_boot_exact_v14218',boot.version==='142.18'&&boot.db==='ldc_user_v1'&&boot.dbver===4,boot);
 ck('hosted_service_worker_scope_nested_ldc_only',boot.registrations.length===1&&boot.registrations[0].scope===APP,boot.registrations);
 ck('hosted_manifest_relative_identity_correct',boot.manifestUrl===APP+'manifest.json',boot.manifestUrl);
 ck('hosted_semantic_model_lazy_on_initial_boot',boot.semanticReady===false,boot.semanticReady);
 await rootpg.reload({waitUntil:'domcontentloaded',timeout:60000});
 ck('hosted_neutral_root_has_no_controlling_ldc_worker',await rootpg.evaluate(()=>navigator.serviceWorker.controller==null));
 // This is an intentional proof of origin-wide IndexedDB access in a disposable profile.
 await pg.evaluate(async()=>await dbPut('settings',{key:'__R13_EPHEMERAL_SCOPE_TEST',val:'QA_ONLY_DO_NOT_KEEP'}));
 const fromRoot=await rootpg.evaluate(async()=>new Promise((resolve,reject)=>{
  const r=indexedDB.open('ldc_user_v1');r.onerror=()=>reject(r.error);
  r.onsuccess=()=>{const db=r.result;try{const t=db.transaction('settings','readonly'),q=t.objectStore('settings').get('__R13_EPHEMERAL_SCOPE_TEST');
   q.onsuccess=()=>{resolve(q.result?.val||null);db.close()};q.onerror=()=>reject(q.error)}
   catch(e){reject(e)}}
 }));
 ck('E19_same_origin_storage_collision_REPRODUCED_on_fresh_test_profile',fromRoot==='QA_ONLY_DO_NOT_KEEP',{same_origin_proof:fromRoot});
 await pg.evaluate(async()=>await dbDelete('settings','__R13_EPHEMERAL_SCOPE_TEST'));
 // A lexical search and real results.
 await pg.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
 await pg.waitForFunction(()=>!searchBusyGeneration,null,{timeout:160000});
 const lexical=await pg.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,busy:!!searchBusyGeneration}));
 ck('hosted_real_words_search_returns_results',lexical.cards>0&&!lexical.busy,lexical);
 // Real semantic model on actual hosted resources — cannot infer from file existence.
 const query="Deuxième, il ne faut pas regarder le passé. Le passé est passé et il faut vivre dans le présent. Ce n'est pas utile du tout de regarder dans le passé. C'est un affront à Jésus. C'est le deuxième texte.";
 await pg.evaluate(async q=>{setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},query);
 await pg.waitForFunction(()=>!searchBusyGeneration,null,{timeout:270000});
 const semantic=await pg.evaluate(()=>({top:searchLastPayload?.payload?.results?.[0]?.entry_id||null,model:typeof LDCPLSV16Runtime!=='undefined'&&LDCPLSV16Runtime.status().ready,
   cards:document.querySelectorAll('#search-results .result-card').length,error:document.getElementById('search-results')?.innerText?.slice(0,300)||''}));
 ck('hosted_real_semantic_search_finds_qualified_intended_passage',semantic.top==='ldc_t09_1909_11_02_e001'&&semantic.model&&semantic.cards===20,semantic);
 if(semantic.cards){
  await pg.locator('#search-results .result-card').first().click();
  await pg.waitForFunction(()=>document.querySelector('#screen-reader')?.classList.contains('active'),null,{timeout:90000});
  const before=await pg.evaluate(()=>({text:document.querySelector('#reader-body')?.innerText?.trim().length||0,height:document.getElementById('reader-scroll')?.clientHeight||0,entry:currentEntry?.id}));
  await pg.setViewportSize({width:844,height:390});await pg.waitForTimeout(1100);
  const after=await pg.evaluate(()=>({text:document.querySelector('#reader-body')?.innerText?.trim().length||0,height:document.getElementById('reader-scroll')?.clientHeight||0,entry:currentEntry?.id,visible:document.querySelector('#screen-reader')?.classList.contains('active')}));
  ck('hosted_mobile_viewport_rotation_does_not_blank_Reader',before.text>100&&after.text>100&&after.height>45&&after.visible,{before,after});
  await pg.setViewportSize({width:390,height:844});
  await pg.locator('#reader-back-btn').click();
  await pg.waitForFunction(()=>document.querySelector('#screen-search')?.classList.contains('active'),null,{timeout:90000});
  try{await pg.waitForFunction(()=>document.querySelectorAll('#search-results .result-card').length===20,null,{timeout:30000})}catch(e){}
  const ret=await pg.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,q:searchQueryDraftCanonical(),screen:document.querySelector('.screen.active')?.id}));
  ck('hosted_Reader_return_restores_search_query_and_results',ret.cards===20&&ret.q===query&&ret.screen==='screen-search',ret);
 }else{
  ck('hosted_mobile_viewport_rotation_does_not_blank_Reader',false,'NO_RESULTS_TO_OPEN');
  ck('hosted_Reader_return_restores_search_query_and_results',false,'NO_READER_OPEN');
 }
 const status=await pg.evaluate(async()=>{
  try{const s=await requestOfflineStatus();return {state:s.state,total:s.total,completed:s.completed}}catch(e){return {err:String(e)}}
 });
 ck('hosted_offline_manifest_count_204',status.total===204,status);
 ck('no_unhandled_js_errors_in_hosted_browser',errors.length===0,{errors:errors.slice(0,12),networkFailures:requestFailures.slice(0,12)});
 report.status=Object.values(report.checks).every(Boolean)?'PASS_HOSTED_REMOTE_BYTES_AND_REAL_CHROME_SCOPED':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_R13_MASSFINDERBETA_HOSTED_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,checks:report.checks,errors:report.errors,warnings:report.warnings},null,2));
 if(browser)await browser.close().catch(()=>{});}
if(report.status==='NOT_RUN')process.exitCode=1;
