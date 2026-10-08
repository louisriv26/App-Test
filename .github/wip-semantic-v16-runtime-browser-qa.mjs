import fs from 'node:fs';import cp from 'node:child_process';import crypto from 'node:crypto';import {chromium} from 'playwright-core';
const PORT=Number(process.env.PLS_V16_RUNTIME_QA_PORT||8870),ROOT='.',BASE='http://127.0.0.1:'+PORT;
const PACK_ID='ldc-pls-v16-current-v14215-enriched-96-72-r1',MANIFEST_SHA='37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0';
const ok=(c,m)=>{if(!c)throw new Error(m)},sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8')),evidence=JSON.parse(fs.readFileSync('pls_v16/evidence/calibration_evidence_v2.json','utf8'));
ok(sha('pls_v16/semantic_pack_manifest.json')===MANIFEST_SHA,'MANIFEST_HASH');
ok(evidence.status==='PASS_QUALIFIABLE','EVIDENCE_STATUS');
const server=cp.spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:ROOT,stdio:['ignore','ignore','inherit']});let browser=null;
const report={schema:'ldc-pls-v16-runtime-browser-qa-v1',status:'UNKNOWN',checks:{},details:{},deployment_authorized:false,hosted_app_test_authorized:false};
try{
 await new Promise(r=>setTimeout(r,900));
 const exe=process.env.CHROME_PATH||'/usr/bin/google-chrome';ok(fs.existsSync(exe),'CHROME_NOT_FOUND');
 browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});
 const ctx=await browser.newContext({serviceWorkers:'block'}),page=await ctx.newPage();page.setDefaultTimeout(180000);
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push('console:'+m.text());});
 await page.goto(BASE+'/.github/wip-semantic-v16-runtime-browser-qa.html',{waitUntil:'load',timeout:30000});
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='ready'&&globalThis.LDCPLSV16Runtime);
 const boot=await page.evaluate(async()=>({
   status:LDCPLSV16Runtime.status(),
   old_owner:typeof LDCPLSOwnerPrototypeV15!=='undefined',
   old_registry:typeof LDCSemanticPackRegistryV5!=='undefined',
   old_guard:typeof LDCSemanticPackGuardR3!=='undefined',
   databases:indexedDB.databases?await indexedDB.databases():[]
 }));
 report.details.boot=boot;
 report.checks.lazy_unverified_boot=boot.status.available===false&&boot.status.ready===false&&boot.status.can_initialize===true&&boot.status.model_ready===false&&boot.status.persistent_semantic_storage===false;
 report.checks.old_runtime_absent=!boot.old_owner&&!boot.old_registry&&!boot.old_guard;
 const ticker=setInterval(()=>process.stdout.write(JSON.stringify({phase:'runtime-init',at:new Date().toISOString()})+'\n'),20000);
 let ready;try{ready=await page.evaluate(()=>LDCPLSV16Runtime.init());}finally{clearInterval(ticker);}
 report.details.ready=ready;
 report.checks.guard_qualified_runtime=ready.available===true&&ready.ready===true&&ready.calibration_status==='QUALIFIED'&&ready.pack_id===PACK_ID&&ready.model_ready===true&&ready.persistent_semantic_storage===false&&ready.registry&&ready.registry.calibration_status==='QUALIFIED';
 const afterDb=await page.evaluate(async()=>indexedDB.databases?await indexedDB.databases():[]);
 report.details.databases_after=afterDb;
 report.checks.no_semantic_indexeddb=afterDb.every(x=>!String(x.name||'').includes('ldc-search-v3-semantic-packs'))&&JSON.stringify(afterDb)===JSON.stringify(boot.databases);

 const positiveResults=[];
 for(const q of protocol.positives){
   const res=await page.evaluate(async x=>await LDCPLSV16Runtime.search(x.text,{sourceMode:'enriched'}),q);
   const rank=res.results.findIndex(x=>String(x.entry_id)===String(q.target_entry_id))+1;
   const expected=evidence.positives.find(x=>x.id===q.id);
   const navOk=res.results.length>0&&res.results.every(x=>Array.isArray(x.source_spans)&&x.source_spans.length>0&&x.passage_id&&x.entry_id&&x.text);
   positiveResults.push({id:q.id,rank,expected_rank:expected.target_rank,state:res.confidence.state,top_entry_id:res.results[0]?.entry_id||null,navigation_metadata_complete:navOk});
 }
 report.details.positives=positiveResults;
 report.checks.owner_queries_match_qualified_evidence=positiveResults.length===3&&positiveResults.every(x=>x.rank===x.expected_rank&&x.state==='possible');
 report.checks.result_navigation_metadata_complete=positiveResults.every(x=>x.navigation_metadata_complete);

 const blind=[];
 for(const q of protocol.blind_holdout_negatives){
   const res=await page.evaluate(async x=>await LDCPLSV16Runtime.search(x.text,{sourceMode:'enriched'}),q);
   const expected=evidence.blind_holdout_negatives.find(x=>x.id===q.id);
   blind.push({id:q.id,state:res.confidence.state,result_count:res.results.length,expected_state:expected.decision.state,top_dense_score:res.confidence.features?.top_dense_score??null});
 }
 report.details.blind=blind;
 report.checks.v2_blind_queries_abstain=blind.length===4&&blind.every(x=>x.state==='abstain'&&x.result_count===0&&x.expected_state==='abstain');

 const truthProbe=protocol.revealed_truth_neutral_probes.find(x=>x.id==='V1-HOLD-02');
 const tr=await page.evaluate(async x=>await LDCPLSV16Runtime.search(x.text,{sourceMode:'enriched'}),truthProbe);
 report.details.truth_neutral_probe={state:tr.confidence.state,label:tr.confidence.label,top_entry_id:tr.results[0]?.entry_id||null,result_count:tr.results.length};
 report.checks.truth_neutral_corrective_retrieval=tr.confidence.state==='possible'&&tr.confidence.label==='Quelques pistes possibles'&&tr.results.length>0&&tr.results[0].entry_id==='LDC.T18.E0010';

 const jesus=await page.evaluate(async x=>await LDCPLSV16Runtime.search(x,{sourceMode:'enriched',jesus:true}),protocol.positives[0].text);
 report.details.jesus_filter={state:jesus.confidence.state,result_count:jesus.results.length};
 report.checks.jesus_filter_executes=jesus&&jesus.pack_id===PACK_ID&&['possible','abstain'].includes(jesus.confidence.state);

 // Verify the real returned passage IDs against the independently hashed, frozen speaker mask.
 // The verified pack Guard binds sequential PLS16 IDs to mask row indices.
 const jesusMask=fs.readFileSync('pls_v16/pack/jesus_mask.bits');
 const jesusEligible=x=>{
   const m=/^PLS16-E-96-72-(\\d{6})$/.exec(String(x&&x.passage_id||''));
   const row=m?Number(m[1])-1:-1;
   return row>=0&&row<22873&&!!(jesusMask[row>>3]&(1<<(row&7)));
 };
 const eligibleResults=(jesus.results||[]).map(x=>({passage_id:x.passage_id,entry_id:x.entry_id,mask_eligible:jesusEligible(x)}));
 report.details.jesus_eligibility={checked:eligibleResults.length,all_eligible:eligibleResults.every(x=>x.mask_eligible),rows:eligibleResults};
 report.checks.jesus_filter_mask_correct=eligibleResults.length>0&&eligibleResults.every(x=>x.mask_eligible);
 
 // Separate falsification challenge: a row excluded by the mask must be rejected
 // by both retrieval lanes, even if it contains the query terms and scores highly.
 const Core=(await import('../search_semantic_v3_core_r4.js')).default||globalThis.LDCSearchSemanticV3R4;
 const Hybrid=(await import('../search_semantic_hybrid_r6.js')).default||globalThis.LDCSemanticHybridR6;
 const toyPassages=[
   {passage_id:'toy-allowed',entry_id:'toy-a',mode:'enriched',volume:1,text:'amour lumière promesse',source_spans:[]},
   {passage_id:'toy-rejected',entry_id:'toy-b',mode:'enriched',volume:1,text:'amour lumière promesse',source_spans:[]}
 ];
 const toyMask=Uint8Array.from([1]);
 const toyDense=Core.createIndex({passages:toyPassages,dim:2,vectors:Float32Array.from([1,0,1,0]),jesusBits:toyMask});
 const toyBm25=Hybrid.buildBm25(toyPassages,toyMask);
 const d0=toyDense.denseSearch(Float32Array.from([1,0]),{sourceMode:'enriched',candidatePool:2,maxResults:2});
 const d1=toyDense.denseSearch(Float32Array.from([1,0]),{sourceMode:'enriched',candidatePool:2,maxResults:2,jesus:true});
 const b0=Hybrid.bm25Search(toyBm25,'amour lumière',{sourceMode:'enriched',maxCandidates:2});
 const b1=Hybrid.bm25Search(toyBm25,'amour lumière',{sourceMode:'enriched',maxCandidates:2,jesus:true});
 const ids=x=>x.map(r=>r.entry_id);
 report.details.jesus_negative_control={dense_unfiltered:ids(d0.dense_candidates),dense_filtered:ids(d1.dense_candidates),bm25_unfiltered:ids(b0.results),bm25_filtered:ids(b1.results)};
 report.checks.jesus_filter_excludes_negative_control=d0.dense_candidates.length===2&&d1.dense_candidates.length===1&&d1.dense_candidates[0].entry_id==='toy-a'&&b0.results.length===2&&b1.results.length===1&&b1.results[0].entry_id==='toy-a';
 


 // Prove the browser error gate remains sensitive to genuine page console errors,
 // while keeping the deliberate challenge off the qualified runtime page.
 const challenge=await ctx.newPage(),seen=[];
 challenge.on('console',m=>{if(m.type()==='error')seen.push('console:'+m.text())});
 challenge.on('pageerror',e=>seen.push('page:'+String(e)));
 await challenge.evaluate(()=>{console.error('QA_INTENTIONAL_ERROR_SENTINEL');setTimeout(()=>{throw Error('QA_INTENTIONAL_PAGEERROR_SENTINEL')},0)});
 await challenge.waitForFunction(()=>false,null,{timeout:300}).catch(()=>{});
 report.details.browser_error_detector_control={console:seen.some(x=>x.includes('QA_INTENTIONAL_ERROR_SENTINEL')),pageerror:seen.some(x=>x.includes('QA_INTENTIONAL_PAGEERROR_SENTINEL'))};
 report.checks.browser_error_detector_sensitive=report.details.browser_error_detector_control.console&&report.details.browser_error_detector_control.pageerror;
 await challenge.close();
 const finalStatus=await page.evaluate(()=>LDCPLSV16Runtime.status());
 report.details.final_status=finalStatus;report.details.browser_errors=errors;
 report.checks.no_browser_errors=errors.length===0;
 report.checks.final_status_stable=finalStatus.available===true&&finalStatus.model_ready===true&&finalStatus.pack_id===PACK_ID;

 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
 fs.writeFileSync('wip-pls-v16-runtime-browser-qa.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 if(report.status!=='PASS')process.exitCode=1;
}finally{if(browser)await browser.close().catch(()=>{});server.kill('SIGTERM');}
