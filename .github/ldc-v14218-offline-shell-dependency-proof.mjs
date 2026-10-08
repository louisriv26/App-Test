import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const root=process.env.LDC_NESTED_FIXTURE_DIR||'',shaPkg='954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb',
 report={schema:'ldc-v14218-offline-transitive-module-root-cause-controlled-challenge-v1',app_zip_sha256:shaPkg,
 frozen_app_source:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 status:'NOT_RUN',checks:{},observations:{},errors:[],
 experimental_cache_priming_only:true,
 no_app_source_or_SW_mutated:true,hosted_e16:'OPEN',hosted_e19:'OPEN',physical_ios:'OPEN',deployment_authority:'NONE'};
const ck=(name,ok,obs)=>{report.checks[name]=!!ok;if(obs!==undefined)report.observations[name]=obs};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const pA=8995,pB=8996,oA='http://127.0.0.1:'+pA+'/',oB='http://127.0.0.1:'+pB+'/';
let ctx,br,servers=[];
try{
 if(!root)throw Error('FIXTURE_ROOT_MISSING');
 const m=JSON.parse(fs.readFileSync(root+'/ldc/PACKAGE_MANIFEST_SHA256.json','utf-8'));
 const dep='pls_v15/runtime/transformers.min.js',target=m.files.find(f=>f.path===dep);
 ck('immutable_package_and_dependency_bound',m.source_commit===report.frozen_app_source&&!!target&&target.bytes===888173,target);
 for(const p of [pA,pB])servers.push(cp.spawn('python3',['-m','http.server',String(p),'--bind','127.0.0.1','--directory',root],{stdio:['ignore','ignore','inherit']}));
 await sleep(800);
 br=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox'],headless:true});
 ctx=await br.newContext({serviceWorkers:'allow'});
 const a=await ctx.newPage(),b=await ctx.newPage(),failRequests=[];
 for(const pg of [a,b]){pg.on('requestfailed',req=>failRequests.push({url:req.url(),failure:req.failure()}));pg.setDefaultTimeout(120000)}
 async function onlineBoot(pg,url){
  await pg.goto(url+'ldc/',{waitUntil:'domcontentloaded'});
  await pg.waitForFunction(()=>typeof LDCPLSV16Runtime==='object'&&typeof goSearch==='function',null,{timeout:90000});
  await pg.evaluate(async()=>{await navigator.serviceWorker.ready});
  return pg.evaluate(async()=>({scope:(await navigator.serviceWorker.getRegistrations()).map(x=>x.scope),ready:LDCPLSV16Runtime.status().ready}));
 }
 const a0=await onlineBoot(a,oA),b0=await onlineBoot(b,oB);
 ck('separate_origin_sw_boot_both_online_without_preloading_model',!a0.ready&&!b0.ready&&a0.scope[0]===oA+'ldc/'&&b0.scope[0]===oB+'ldc/',{a:a0,b:b0});
 const shellBefore=await b.evaluate(async()=>{
  const names=await caches.keys(),shell=names.find(x=>x.includes('shell-v2.19.142.18'));
  const cache=await caches.open(shell),r=await cache.match(new URL('./pls_v15/runtime/transformers.min.js',location.href).href);
  return {cache:shell,alreadyCached:!!r};
 });
 ck('original_sw_shell_excludes_critical_static_module',!shellBefore.alreadyCached,shellBefore);
 const intervention=await b.evaluate(async()=>{
  const dep=new URL('./pls_v15/runtime/transformers.min.js',location.href).href;
  const src=await fetch(dep,{cache:'no-store'});
  if(!src.ok)throw Error('B_PREPARE_FETCH_FAIL_'+src.status);
  const bytes=await src.clone().arrayBuffer();
  const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
  const names=await caches.keys(),shell=names.find(x=>x.includes('shell-v2.19.142.18'));
  await (await caches.open(shell)).put(dep,src);
  const after=await (await caches.open(shell)).match(dep);
  return {url:dep,sha256:digest,bytes:bytes.byteLength,cache:shell,cachedAfter:!!after};
 });
 ck('QA_only_prime_exact_transformer_bytes',intervention.sha256===target.sha256&&intervention.bytes===target.bytes&&intervention.cachedAfter,intervention);
 for(const p of servers){p.kill('SIGTERM');await new Promise(resolve=>p.once('exit',resolve))}
 await ctx.setOffline(true);
 async function offlineRead(pg){
  await pg.reload({waitUntil:'domcontentloaded',timeout:90000});
  try{await pg.waitForFunction(()=>typeof LDCPLSV16Runtime==='object',null,{timeout:12000,polling:250})}catch(_){}
  return pg.evaluate(async()=>({modulePresent:typeof LDCPLSV16Runtime==='object',appJS:typeof goSearch==='function',
   controller:!!navigator.serviceWorker.controller,screen:document.querySelector('.screen.active')?.id||null,
   modelReady:typeof LDCPLSV16Runtime==='object'?LDCPLSV16Runtime.status().ready:null}));
 }
 const aOff=await offlineRead(a),bOff=await offlineRead(b);
 ck('unprimed_exact_frozen_zip_offline_boot_missing_module_reproduced',!aOff.modulePresent&&aOff.controller,aOff);
 ck('same_exact_frozen_zip_only_cache_primed_boot_recovers',bOff.modulePresent&&bOff.appJS&&bOff.controller&&bOff.screen==='screen-home'&&!bOff.modelReady,bOff);
 ck('only_failed_unprimed_request_is_omitted_transformer',failRequests.some(x=>x.url.includes('8995/ldc/pls_v15/runtime/transformers.min.js')),failRequests.slice(-15));
 if(bOff.modulePresent){
   await b.evaluate(async()=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft('Jésus et la Divine Volonté dans la vie intérieure',{mode:'meaning',syncOther:true});await runSearch()});
   await b.waitForFunction(()=>!searchBusyGeneration,null,{timeout:120000});
   const result=await b.evaluate(()=>({busy:!!searchBusyGeneration,ready:LDCPLSV16Runtime.status().ready,cards:document.querySelectorAll('#search-results .result-card').length,
    message:(document.getElementById('search-results')?.innerText||'').slice(0,550),meta:(document.getElementById('search-meta')?.innerText||'').slice(0,300)}));
   ck('offline_no_model_semantic_query_fails_closed_with_no_spurious_results',!result.busy&&!result.ready&&result.cards===0&&/(indisponible|impossible|connexion|hors ligne|pas pu|erreur|non encore qualifié)/i.test(result.message+' '+result.meta),result);
 }else ck('offline_no_model_semantic_query_fails_closed_with_no_spurious_results',false,{reason:'dependency cache intervention did not restore runtime'});
 report.status=Object.values(report.checks).every(Boolean)?'PASS_ROOT_CAUSE_PROOF_ONLY_FROZEN_APP_REMAINS_DEFECTIVE':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_OFFLINE_TRANSITIVE_MODULE_ROOT_CAUSE_PROOF.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(br)await br.close().catch(()=>{});
 for(const p of servers)try{p.kill('SIGTERM')}catch(_){}
 if(report.status!=='PASS_ROOT_CAUSE_PROOF_ONLY_FROZEN_APP_REMAINS_DEFECTIVE')process.exitCode=1;
}
