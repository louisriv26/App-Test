import fs from 'node:fs';
import crypto from 'node:crypto';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const DIR=process.env.LDC_PACKAGE_EXTRACT_DIR||'';
const ZIP=process.env.LDC_PACKAGE_ZIP_PATH||'';
const EXPECT='954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb';
const report={schema:'ldc-v14218-exact-archived-zip-runtime-real-chrome-v1',
 artifact_app_zip_sha256:EXPECT,source_built_commit:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 status:'NOT_TESTED',checks:{},details:{},errors:[],
 scopes:'EXACT UNRELEASED ZIP EXTRACTED TO FRESH LOCALHOST CHROMIUM; NOT HOSTED, NOT IOS',
 app_test_deployment_authority:'NONE',production_deployment_authority:'NONE'};
const ck=(k,c,d)=>{report.checks[k]=!!c;if(d!==undefined)report.details[k]=d};
let proc,browser;const port=8981,base='http://127.0.0.1:'+port+'/';
try{
 if(!DIR||!ZIP)throw Error('EXACT_PACKAGING_INPUTS_MISSING');
 const h=crypto.createHash('sha256'),stream=fs.createReadStream(ZIP);
 for await(const b of stream)h.update(b);
 const actual=h.digest('hex');
 ck('exact_archived_zip_matches_frozen_sha',actual===EXPECT,{actual,expected:EXPECT});
 const manifest=JSON.parse(fs.readFileSync(DIR+'/PACKAGE_MANIFEST_SHA256.json','utf8'));
 ck('source_commit_in_package_manifest',manifest.source_commit==='7c292d6221bb350fac3aeaa83750b8784706d45c',{source:manifest.source_commit,entries:manifest.files.length});
 ck('package_manifest_is_WIP_no_deploy',manifest.files.length===273&&manifest.app_test_authority==='NONE'&&manifest.production_authority==='NONE');
 proc=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',DIR],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,1000));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'}),page=await context.newPage();
 page.setDefaultTimeout(180000);
 page.on('pageerror',e=>report.errors.push('PAGE_ERROR:'+String(e)));
 page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP_'+r.status()+':'+r.url())});
 await page.goto(base,{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none'&&!!window.LDCPLSV16Runtime,null,{timeout:120000});
 await page.evaluate(()=>{if(document.getElementById('onboarding-overlay')&&getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 const boot=await page.evaluate(()=>({public:PUBLIC_VERSION,modelLoaded:LDCPLSV16Runtime.status().ready,db:DB_NAME}));
 ck('fresh_exact_zip_boots_and_lazy_model',boot.public==='142.18'&&!boot.modelLoaded&&boot.db==='ldc_user_v1',boot);
 const sw=await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;const c=await caches.keys();return {active:!!r.active,scope:r.scope,shell:c.filter(x=>x.includes('shell-v2.19.142.18'))}});
 ck('exact_zip_sw_installs_coherent_revision',sw.active&&sw.shell.length===1,sw);
 const query="Deuxième, il ne faut pas regarder le passé. Le passé est passé et il faut vivre dans le présent. Ce n'est pas utile du tout de regarder dans le passé. C'est un affront à Jésus. C'est le deuxième texte.";
 await page.evaluate(async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},query);
 await page.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
 const search=await page.evaluate(()=>({status:LDCPLSV16Runtime.status(),first:searchLastPayload.payload.results[0]?.entry_id,
   resultCount:searchLastPayload.payload.results.length,confidence:searchLastPayload.payload.confidence.state,
   cards:document.querySelectorAll('#search-results .result-card').length}));
 ck('exact_zip_real_semantic_model_working',search.status.ready&&search.first==='ldc_t09_1909_11_02_e001'&&search.confidence==='possible'&&search.cards===20,{first:search.first,count:search.resultCount,confidence:search.confidence});
 await page.locator('#search-results .result-card').first().click();
 await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:90000});
 const reader=await page.evaluate(()=>({entry:currentEntry?.id,body:document.getElementById('reader-body')?.innerText?.length||0,height:document.getElementById('reader-scroll')?.clientHeight||0}));
 ck('exact_zip_search_opens_correct_reader',reader.entry===search.first&&reader.body>0&&reader.height>=65,reader);
 await page.locator('#reader-back-btn').click();
 await page.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active')&&!searchBusyGeneration,null,{timeout:180000});
 const back=await page.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,query:searchQueryDraftCanonical()}));
 ck('exact_zip_Reader_Return_reinstates_semantic_results',back.cards===20&&back.query===query,{cards:back.cards,queryMatches:back.query===query});
 ck('no_page_or_404_errors',report.errors.length===0,report.errors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS_EXACT_PACKAGED_ZIP_ACTUAL_CHROMIUM':'FAIL';
}catch(e){report.status='FAIL';report.errors.push('HARNESS_OR_RUNTIME:'+String(e.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_EXACT_WIP_ZIP_ACTUAL_CHROMIUM_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(proc)proc.kill('SIGTERM');
 if(report.status!=='PASS_EXACT_PACKAGED_ZIP_ACTUAL_CHROMIUM')process.exitCode=1;
}
