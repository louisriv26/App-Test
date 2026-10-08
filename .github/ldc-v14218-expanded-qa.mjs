import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const report={schema:'ldc-v14218-expanded-actual-app-dom-v1',status:'UNKNOWN',source_sha:process.env.GITHUB_SHA||null,
  checks:{},results:{},errors:[],open_gates:['HOSTED_E16_E19','PHYSICAL_SAFARI','WEBKIT','PWA','OFFLINE_204_CORPUS','VOICEOVER','LONG_RUN_MEMORY']};
const b='http://127.0.0.1:8897';
let server,browser;
const test=(id,ok,v)=>{report.checks[id]=!!ok;if(v!==undefined)report.results[id]=v};
try{
 server=cp.spawn('python3',['-m','http.server','8897','--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,850));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
 const page=await context.newPage();page.setDefaultTimeout(180000);
 page.on('pageerror',e=>report.errors.push('JS:'+String(e)));
 page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP_'+r.status()+':'+r.url())});
 await page.goto(b,{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none'&&!!window.LDCPLSV16Runtime,null,{timeout:120000});
 await page.evaluate(()=>{if(getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 let w=await page.evaluate(()=>({version:PUBLIC_VERSION,pack:window.LDCPLSV16Runtime.status(),sw:SW_CACHE_VERSION,mode:supplementMode}));
 test('new_identity_v142_18',w.version==='142.18'&&w.sw.includes('142.18'),{version:w.version,sw:w.sw});
 test('semantic_lazy_boot',w.pack.ready===false);
 await page.evaluate(async()=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft('tome 9',{mode:'meaning',syncOther:true});await runSearch()});
 await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:120000});
 const structural=await page.evaluate(()=>({pack:window.LDCPLSV16Runtime.status(),semantic:!!searchLastPayload?.semantic,text:document.getElementById('search-meta')?.textContent}));
 test('structural_only_uses_v2_lazily',structural.pack.ready===false&&structural.semantic===false,structural);
 const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8'));
 async function search(q,intent='meaning'){
  await page.evaluate(async ({q,intent})=>{
    await goSearch();setSearchIntentMode(intent,{rerun:false,persist:false});
    setSearchQueryDraft(q,{mode:intent,syncOther:true});
    await runSearch();
  },{q,intent});
  await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:180000});
  return page.evaluate(()=>({
    semantic:!!searchLastPayload?.semantic,
    payload:searchLastPayload?.payload||null,
    counts:searchLastPayload?.matchCounts||null,
    cards:document.querySelectorAll('#search-results .result-card').length,
    snippets:document.getElementById('search-results')?.innerText?.slice(0,260)||'',
    heap:performance.memory?.usedJSHeapSize||null
  }));
 }
 for(const p of protocol.positives.slice(0,3)){
   const a=await search(p.text),rank=a.payload?.results?.findIndex(x=>x.entry_id===p.target_entry_id)+1||0;
   test('positive_'+p.id,a.semantic&&a.payload?.confidence?.state==='possible'&&rank>=1&&rank<=10,
     {rank,target:p.target_entry_id,count:a.payload?.results?.length,state:a.payload?.confidence?.state,heap:a.heap});
 }
 for(const n of protocol.development_negatives.slice(0,4)){
   const a=await search(n.text);
   test('negative_'+n.id,a.semantic&&a.payload?.confidence?.state==='abstain',{state:a.payload?.confidence?.state,count:a.payload?.results?.length});
 }
 const metadata=fs.readFileSync('pls_v16/pack/metadata.jsonl','utf8').trimEnd().split(/\r?\n/),passageMap=new Map();
 metadata.forEach((x,i)=>{const p=JSON.parse(x);passageMap.set(String(p.passage_id),i)});
 const mask=fs.readFileSync('pls_v16/pack/jesus_mask.bits');
 await page.evaluate(()=>{searchSpeakerFilter=true;renderSpeakerFilterRow();});
 let masked=await search(protocol.positives[1].text);
 // Browser-level count and direct bound runtime filter; both must enforce mask if results exist.
 const runtime=await page.evaluate(async q=>window.LDCPLSV16Runtime.search(q,{sourceMode:'enriched',jesus:true,maxResults:20}),protocol.positives[1].text);
 const allowed=x=>{const row=passageMap.get(String(x.passage_id));return Number.isInteger(row)&&!!(mask[row>>3]&(1<<(row&7)))};
 const maskRows=runtime.results||[];
 test('jesus_mask_filter_applied_all_returned_rows',maskRows.length>0&&maskRows.every(allowed),
  {items:maskRows.length,all_allowed:maskRows.every(allowed),confidence:runtime.confidence?.state,ui_results:masked.payload?.results?.length});
 // Reset speaker before lexical, to distinguish user intent from source restrictions.
 await page.evaluate(()=>{searchSpeakerFilter=false;renderSpeakerFilterRow();});
 const lexical=await search('volonté chlorophylle','words');
 const action=page.getByRole('button',{name:'Voir les résultats élargis'});
 const available=await action.count();
 const beforeLex=await page.evaluate(()=>({partial:searchLastPayload?.matchCounts?.partial||0,
    lane:searchLastPayload?.foundation?.lane||null,visible:document.getElementById('trust-notice')?.style?.display||null}));
 test('lexical_e20_truthful_partial_action',!lexical.semantic&&beforeLex.partial>0&&available===1,
  {partialCount:beforeLex.partial,cards:lexical.cards,actionCount:available,beforeLex});
 if(available===1){
   await action.click();
   await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:90000});
   const after=await page.evaluate(()=>({lane:searchLastPayload?.foundation?.lane||null,
     cards:document.querySelectorAll('#search-results .result-card').length,trust:getComputedStyle(document.getElementById('trust-notice')).display}));
   test('lexical_partial_expansion_shows_results',after.cards>0&&after.trust!=='none',after);
 }
 const last=await page.evaluate(()=>({memory:performance.memory?.usedJSHeapSize||null,
   pack:window.LDCPLSV16Runtime.status(),version:PUBLIC_VERSION}));
 report.results.end_state={heap_last:last.memory,ready:last.pack.ready,version:last.version};
 test('semantic_pack_still_ready_after_mode_switch',last.pack.ready===true);
 test('no_unhandled_browser_errors',report.errors.length===0,report.errors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.errors.push('SCRIPT_OR_APP:'+String(e.stack||e));report.status='FAIL'}
finally{
 fs.writeFileSync('LDC_v142.18_EXPANDED_ACTUAL_DOM_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
