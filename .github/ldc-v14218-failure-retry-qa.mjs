import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const report={schema:'ldc-v14218-failure-retry-actual-app-dom-v1',status:'UNKNOWN',checks:{},details:{},errors:[],source_sha:process.env.GITHUB_SHA||null,deployment:'NONE'};
const port=8894,base='http://127.0.0.1:'+port;
let server,browser;
try{
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
 const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8'));
 const knownPositive=protocol.positives.find(x=>x.id==='OWNER-REAL-02');
 if(!knownPositive)throw Error('KNOWN_FROZEN_OWNER_QUERY_MISSING');
 const page=await context.newPage();
 page.setDefaultTimeout(90000);
 let failureCount=0, manifestRequests=0;
 await page.route('**/pls_v16/semantic_pack_manifest.json',async route=>{
   manifestRequests++;if(failureCount<1){failureCount++;await route.fulfill({status:503,body:'INTENTIONAL_MODEL_MANIFEST_FAILURE'});}
   else await route.continue();
 });
 page.on('pageerror',e=>report.errors.push('pageerror '+String(e)));
 await page.goto(base+'/',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none'&&window.LDCPLSV16Runtime,null,{timeout:120000});
 await page.evaluate(()=>{if(getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 await page.evaluate(async q=>{
   await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});
   setSearchQueryDraft(q,{mode:'meaning',syncOther:true});
   await runSearch();
 },knownPositive.text);
 await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:90000});
 const afterFail=await page.evaluate(()=>({pack:window.LDCPLSV16Runtime.status(),
   user_text:document.getElementById('search-results')?.innerText,
   meta:document.getElementById('search-meta')?.innerText,
   query:searchQueryDraftCanonical(),payload:!!searchLastPayload}));
 report.details.after_initial_failure={phase:afterFail.pack,interface:afterFail.user_text,meta:afterFail.meta,query:afterFail.query};
 report.checks.failure_does_not_fabricate_results=!afterFail.payload;
 report.checks.user_query_preserved=afterFail.query===knownPositive.text;
 await page.evaluate(async()=>{await runSearch();});
 await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:90000});
 const retried=await page.evaluate(()=>({pack:window.LDCPLSV16Runtime.status(),
     results:document.querySelectorAll('#search-results .result-card').length,
     user_text:document.getElementById('search-results')?.innerText,
     payload:!!searchLastPayload?.semantic,first_entry:searchLastPayload?.payload?.results?.[0]?.entry_id||null,confidence:searchLastPayload?.payload?.confidence?.state||null}));
 report.details.after_retry={...retried,manifest_requests:manifestRequests,first_manifest_failed:failureCount};
 report.checks.retry_attempts_manifest_again=manifestRequests>=2;
 report.checks.retry_recovers_without_reload=retried.pack.available===true&&retried.payload&&retried.results>0&&retried.first_entry===knownPositive.target_entry_id&&retried.confidence==='possible';
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e.stack||e))}
finally{
 fs.writeFileSync('LDC_v142.18_FAILURE_RETRY_DOM_EVIDENCE.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
