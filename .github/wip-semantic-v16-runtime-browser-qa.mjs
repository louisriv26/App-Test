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

 const finalStatus=await page.evaluate(()=>LDCPLSV16Runtime.status());
 report.details.final_status=finalStatus;report.details.browser_errors=errors;
 report.checks.no_browser_errors=errors.length===0;
 report.checks.final_status_stable=finalStatus.available===true&&finalStatus.model_ready===true&&finalStatus.pack_id===PACK_ID;

 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
 fs.writeFileSync('wip-pls-v16-runtime-browser-qa.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 if(report.status!=='PASS')process.exitCode=1;
}finally{if(browser)await browser.close().catch(()=>{});server.kill('SIGTERM');}
