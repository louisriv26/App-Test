import fs from 'node:fs';
import { chromium } from 'playwright-core';
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/';
const report={schema:'ldc-v14219-r22-hosted-massfinderbeta-offline-personal-state-browser-v2-outcome-based-semantic',
 tested_at:new Date().toISOString(),app:APP,source_commit:'0542656639432481c32bd70f354a6271b63dd93e',
 status:'NOT_RUN',checks:{},details:{},errors:[],warnings:[],
 scope:'Actual live GitHub Pages MassFinder Beta, fresh isolated Chromium profile, synthetic notes/collections only, no repository/production mutation',
 deployment_authority:'NONE',iPhone_iPad_physical:'OPEN',old_beta_nested_worker_lifecycle:'NOT_TESTED'};
const ck=(key,pass,detail)=>{report.checks[key]=!!pass;if(detail!==undefined)report.details[key]=detail};
let browser,ctx;
try{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'});
 const p=await ctx.newPage(),errors=[],failed=[];
 p.setDefaultTimeout(210000);
 p.on('pageerror',e=>errors.push(String(e)));
 p.on('requestfailed',req=>failed.push({path:req.url().slice(-110),fail:req.failure()}));
 async function boot(){await p.goto(APP,{waitUntil:'domcontentloaded',timeout:100000});
  await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:170000});
  await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
  await p.evaluate(async()=>await navigator.serviceWorker.ready)}
 await boot();
 const state=await p.evaluate(async()=>({version:PUBLIC_VERSION,db:DB_NAME,reg:(await navigator.serviceWorker.getRegistrations()).map(x=>x.scope),
  cacheCount:(await caches.keys()).length,prepared:(await requestOfflineStatus()).state}));
 ck('hosted_real_SW_ready_correct_app_version',state.version==='142.19'&&state.reg.length===1&&state.reg[0]===APP,state);
 // Real IndexedDB use in a throwaway browser context, synthetic data only.
 const seeded=await p.evaluate(async()=>{
  const id=await dbPut('collections',{name:'R22_HOSTED_COLLECTION_DISPOSABLE',ts:Date.now()});
  const item=await dbAddCollectionItemAtomic(id,{
   entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',volume:1,
   stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001',
   note:'R22 synthetic item note (not personally identifiable)',ts:Date.now()});
  const nid=await dbPut('notes',{entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',
   stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001',volume:1,
   text:'R22_HOSTED_PERSONAL_STATE_DUMMY',ts:Date.now()});
  return {collectionId:id,added:item.status,noteId:nid,notes:(await dbGetAll('notes')).length};
 });
 ck('synthetic_collection_and_note_saved_in_hosted_ephemeral_browser',seeded.added==='ADDED'&&seeded.notes===1,seeded);
 const initial=await p.evaluate(async()=>await requestOfflineStatus());
 ck('real_hosted_offline_manifest_has_204_assets',initial.total===204,{state:initial.state,total:initial.total,completed:initial.completed});
 await p.evaluate(async()=>await startOfflinePreparation());
 await p.waitForFunction(()=>['READY','ERROR','PARTIAL'].includes(offlineUiState.state),null,{timeout:1200000,polling:1500});
 const prepared=await p.evaluate(async()=>{const x=await requestOfflineStatus();return {state:x.state,completed:x.completed,total:x.total,failed:x.failed,semanticReady:LDCPLSV16Runtime.status().ready}});
 ck('live_github_pages_prepares_all_204_corpus_assets',prepared.state==='READY'&&prepared.completed===204&&prepared.total===204,prepared);
 ck('hosted_offline_preparation_does_not_eagerly_load_semantic_model',prepared.semanticReady===false,prepared.semanticReady);
 const before=await p.evaluate(async()=>({notes:(await dbGetAll('notes')).map(x=>x.text),
  collections:(await dbGetAll('collections')).map(x=>x.name),
  children:(await dbGetAll('col_items')).length}));
 ck('hosted_persistent_test_data_survived_offline_preparation',before.notes.includes('R22_HOSTED_PERSONAL_STATE_DUMMY')&&before.collections.includes('R22_HOSTED_COLLECTION_DISPOSABLE')&&before.children===1,before);
 await ctx.setOffline(true);
 await p.reload({waitUntil:'domcontentloaded',timeout:160000});
 await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 const cold=await p.evaluate(async()=>{
  const status=await requestOfflineStatus(),counts=[],store={
    notes:(await dbGetAll('notes')).map(x=>x.text),
    collections:(await dbGetAll('collections')).map(x=>x.name),
    colItems:(await dbGetAll('col_items')).length};
  for(const vol of [1,18,36]){await ensureVolumeReaderData(vol);counts.push({volume:vol,entries:corpusCache[vol]?.entries?.length||0})}
  return {loadingHidden:getComputedStyle(document.getElementById('loading')).display==='none',
   controller:navigator.serviceWorker.controller?.scriptURL,status:{state:status.state,completed:status.completed,total:status.total},counts,store};
 });
 ck('hosted_real_offline_reload_from_204_cache',cold.loadingHidden&&cold.controller===APP+'sw.js'&&cold.status.state==='READY'&&cold.status.completed===204,cold);
 ck('hosted_offline_three_tomes_remain_readable',cold.counts.length===3&&cold.counts.every(x=>x.entries>0),cold.counts);
 ck('hosted_personal_state_survives_actual_network_offline_reload',cold.store.notes.includes('R22_HOSTED_PERSONAL_STATE_DUMMY')&&cold.store.collections.includes('R22_HOSTED_COLLECTION_DISPOSABLE')&&cold.store.colItems===1,cold.store);
 await p.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
 await p.waitForFunction(()=>!searchBusyGeneration,null,{timeout:160000});
 const words=await p.evaluate(()=>({results:document.querySelectorAll('#search-results .result-card').length,busy:!!searchBusyGeneration}));
 ck('hosted_offline_par_les_mots_returns_results',words.results>0&&!words.busy,words);
 await p.evaluate(async()=>{setSearchIntentMode('meaning',{rerun:false,persist:false});
  setSearchQueryDraft('Jésus appelle notre volonté à vivre dans la Divine Volonté',{mode:'meaning',syncOther:true});await runSearch()});
 await p.waitForFunction(()=>!searchBusyGeneration,null,{timeout:150000});
 const unready=await p.evaluate(()=>({busy:!!searchBusyGeneration,
  results:document.querySelectorAll('#search-results .result-card').length,
  message:document.getElementById('search-results')?.innerText?.slice(0,400),
  runtimePresent:typeof LDCPLSV16Runtime==='object',semanticReady:typeof LDCPLSV16Runtime==='object'&&LDCPLSV16Runtime.status().ready,
  semanticPayload:searchLastPayload?.semantic===true, top:searchLastPayload?.payload?.results?.[0]?.entry_id||null}));
 const offlineSemanticSucceeded=unready.semanticReady&&unready.semanticPayload&&unready.results===20&&!unready.busy;
 const offlineSemanticTruthfulUnavailable=unready.results===0&&!unready.busy&&/par le sens indisponible/i.test(unready.message||'');
 ck('hosted_offline_semantic_real_20_results_or_truthful_unavailable_no_spurious_lexical_fallback',
  offlineSemanticSucceeded||offlineSemanticTruthfulUnavailable,
  {...unready,adjudication:offlineSemanticSucceeded?'REAL_OFFLINE_SEMANTIC_SUCCESS':offlineSemanticTruthfulUnavailable?'TRUTHFUL_UNAVAILABLE':'INVALID_OFFLINE_RESULT'});
 // After return online, demonstrate the exact notes/corpus remain.
 await ctx.setOffline(false);
 await p.reload({waitUntil:'domcontentloaded',timeout:120000});
 await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:130000});
 const final=await p.evaluate(async()=>({version:PUBLIC_VERSION,status:(await requestOfflineStatus()).state,notes:(await dbGetAll('notes')).length,collections:(await dbGetAll('collections')).length}));
 ck('hosted_online_reopen_after_offline_keeps_all_content_and_user_records',final.version==='142.19'&&final.status==='READY'&&final.notes===1&&final.collections===1,final);
 ck('hosted_offline_and_online_no_unhandled_pageerrors',errors.length===0,{errors,failures:failed.slice(-12)});
 report.status=Object.values(report.checks).every(Boolean)?'PASS_V14219_LIVE_HOSTED_OFFLINE_204_AND_STATE_ONLY':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync('LDC_v142.19_R22_MASSFINDERBETA_HOSTED_OFFLINE_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,checks:report.checks,errors:report.errors},null,2));
 if(browser)await browser.close().catch(()=>{});}
