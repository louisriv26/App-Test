import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const port=8940,base='http://127.0.0.1:'+port;
const report={schema:'ldc-v14218-semantic-cold-warm-return-resource-dom-v1',
 status:'UNKNOWN',source_sha:process.env.GITHUB_SHA||null,checks:{},measurements:{},errors:[],
 scope:'LOCAL_CHROMIUM_ONLY__NOT_PEAK_PROCESS_OR_PHYSICAL_SAFARI',
 deployment_authority:'NONE'};
let server,browser;
const measured=(key,val,obj)=>{report.checks[key]=!!val;if(obj!==undefined)report.measurements[key]=obj};
try{
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
 const page=await ctx.newPage();page.setDefaultTimeout(180000);
 const errors=[],finished=[];
 page.on('pageerror',e=>errors.push('JS:'+String(e)));
 page.on('response',r=>{if(r.status()>=400)errors.push('HTTP_'+r.status()+':'+r.url())});
 page.on('requestfinished',r=>{
   const u=r.url();if(u.includes('/pls_v16/')||u.includes('/pls_v15/'))finished.push({url:u.replace(base+'/',''),time:Date.now()});
 });
 await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none'&&window.LDCPLSV16Runtime,null,{timeout:120000});
 await page.evaluate(()=>{if(getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8'));
 const positive=protocol.positives.find(p=>p.id==='OWNER-REAL-02');
 const resourceMetrics=()=>({
   modelParts:finished.filter(x=>/model_int8\.onnx\.part0[1-4]/.test(x.url)).length,
   distinctModelParts:[...new Set(finished.filter(x=>/model_int8\.onnx\.part0[1-4]/.test(x.url)).map(x=>x.url))].length,
   metadata:finished.filter(x=>x.url.includes('pls_v16/pack/metadata.jsonl')).length,
   vectors:finished.filter(x=>x.url.includes('pls_v16/pack/vectors.i8')).length,
   totalPLSRequests:finished.length,
   distinctResources:[...new Set(finished.map(x=>x.url))].length
 });
 const boot=await page.evaluate(()=>({ready:window.LDCPLSV16Runtime.status().ready,legacy:!!window.LDCPLSOwnerPrototypeV15,
   heap:performance.memory?.usedJSHeapSize||null}));
 measured('cold_boot_lazy_no_legacy_runtime',boot.ready===false&&boot.legacy===false,boot);
 const t0=Date.now();
 await page.evaluate(async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});
   setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},positive.text);
 await page.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
 const coldElapsed=Date.now()-t0;
 const cold=await page.evaluate(target=>({ready:LDCPLSV16Runtime.status().ready,
   confidence:searchLastPayload?.payload?.confidence?.state||null,
   rank:(searchLastPayload?.payload?.results||[]).findIndex(x=>x.entry_id===target)+1,
   n:document.querySelectorAll('#search-results .result-card').length,
   heap:performance.memory?.usedJSHeapSize||null,
   total:performance.memory?.totalJSHeapSize||null}),positive.target_entry_id);
 const resourceCold=resourceMetrics();
 measured('cold_loaded_qualified_pack_and_found_owner_target',cold.ready&&cold.confidence==='possible'&&cold.rank===1&&cold.n>0,{ms:coldElapsed,...cold,network:resourceCold});
 measured('cold_verified_four_static_onnx_parts',resourceCold.distinctModelParts===4&&resourceCold.modelParts>=4&&resourceCold.metadata>0&&resourceCold.vectors>0,resourceCold);
 const t1=Date.now();
 await page.evaluate(async q=>{setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},positive.text);
 await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:180000});
 const warmMs=Date.now()-t1;
 const warm=await page.evaluate(()=>({ready:LDCPLSV16Runtime.status().ready,
   heap:performance.memory?.usedJSHeapSize||null,cards:document.querySelectorAll('#search-results .result-card').length}));
 const resourceWarm=resourceMetrics();
 measured('warm_reuses_existing_model_part_requests',resourceWarm.modelParts===resourceCold.modelParts&&resourceWarm.metadata===resourceCold.metadata&&resourceWarm.vectors===resourceCold.vectors,
   {ms:warmMs,...warm,network:resourceWarm});
 await page.locator('#search-results .result-card').first().click();
 await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:90000});
 const t2=Date.now();
 await page.locator('#reader-back-btn').click();
 await page.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active')&&!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
 const returnMs=Date.now()-t2;
 const returned=await page.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,
   heap:performance.memory?.usedJSHeapSize||null,ready:LDCPLSV16Runtime.status().ready}));
 const resourceReturn=resourceMetrics();
 measured('return_does_not_refetch_frozen_model_parts',resourceReturn.modelParts===resourceCold.modelParts&&returned.ready&&returned.cards>0,
   {ms:returnMs,...returned,network:resourceReturn});
 measured('no_runtime_errors',errors.length===0,errors);
 report.measurements.resource_details={first:(resourceCold),warm:resourceWarm,returned:resourceReturn,
   loaded_urls:[...new Set(finished.map(x=>x.url))],request_note:'Completed browser requests can include HTTP-cache re-reads; they do not establish twice the over-network bytes.',heap_note:'Chromium JS heap is not device peak memory. All memory gates physical OPEN.'};
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.errors.push('HARNESS_OR_APP:'+String(e.stack||e));report.status='FAIL'}
finally{
 fs.writeFileSync('LDC_v142.18_COLD_WARM_RETURN_RESOURCES_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
