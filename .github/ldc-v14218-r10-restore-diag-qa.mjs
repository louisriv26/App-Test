import fs from 'node:fs';
import cp from 'node:child_process';
import crypto from 'node:crypto';
import { chromium } from 'playwright-core';
const dir=process.env.LDC_ARCHIVE_EXTRACT_DIR, port=8998, url='http://127.0.0.1:'+port+'/';
const EXPECT_SHA='954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb';
const report={schema:'ldc-v14218-r10-real-restore-diagnostic-redaction-and-corruption-QA-v1',
  app_zip_sha256:EXPECT_SHA,source_commit:'7c292d6221bb350fac3aeaa83750b8784706d45c',
  status:'NOT_RUN',checks:{},details:{},errors:[],
  scope:'Only exact archived ZIP, local Chromium, synthetic user records, independent fresh browser profiles',
  app_mutation_authority:'NONE',deploy_authority:'NONE',hosted_e16_e19:'OPEN',physical_iphone_ipad:'OPEN'};
const ck=(name,ok,d)=>{report.checks[name]=!!ok;if(d!==undefined)report.details[name]=d};
let browser,server;
try {
 if(!dir||!fs.existsSync(dir+'/PACKAGE_MANIFEST_SHA256.json'))throw Error('EXTRACTED_ARCHIVE_NOT_FOUND');
 const manifest=JSON.parse(fs.readFileSync(dir+'/PACKAGE_MANIFEST_SHA256.json','utf8'));
 ck('exact_package_source_bound',manifest.source_commit===report.source_commit&&manifest.files.length===273,
  {source:manifest.source_commit,files:manifest.files.length});
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',dir],{stdio:['ignore','ignore','inherit']});
 await new Promise(resolve=>setTimeout(resolve,900));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const ctxA=await browser.newContext({serviceWorkers:'allow'}),ctxB=await browser.newContext({serviceWorkers:'allow'});
 const a=await ctxA.newPage(),b=await ctxB.newPage(),errors=[];
 for(const p of [a,b]){p.on('pageerror',e=>errors.push(String(e)));p.setDefaultTimeout(120000)}
 async function boot(p){
  await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForFunction(()=>typeof dbGetAll==='function' && typeof buildUserDataStreamBackup==='function' &&
    typeof parseBackupStreamToStage==='function' && !!db && typeof diagnosticsText==='function',
    null,{timeout:120000});
  return p.evaluate(()=>({app:PUBLIC_VERSION,db:DB_NAME,stores:USER_DATA_STORES.slice()}));
 }
 const [ga,gb]=await Promise.all([boot(a),boot(b)]);
 ck('two_fresh_profiles_same_exact_application_separate_databases',
  ga.app==='142.18'&&gb.app==='142.18'&&ga.db==='ldc_user_v1'&&gb.db===ga.db&&ga.stores.length===8,
  {a:ga,b:gb});
 const secret='R10_PRIVATE_NOTE_SENTINEL_DO_NOT_DISCLOSE_IN_PUBLIC_DIAGNOSTIC';
 const querySentinel='R10_PRIVATE_SEARCH_SENTINEL_DO_NOT_DISCLOSE';
 const refs={entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',
   stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001',volume:1};
 const seededA=await a.evaluate(async data=>{
   const id=await dbPut('collections',{name:'R10 SOURCE COLLECTION',ts:Date.now()});
   const rec=await dbAddCollectionItemAtomic(id,{...data.refs,note:'R10 synthetic collection note',ts:Date.now()});
   const noteId=await dbPut('notes',{...data.refs,text:data.secret,quote:'Synthetic quote',ts:Date.now()});
   await dbPut('settings',{key:'textLevel',val:'grand',ts:Date.now()});
   return {collection:id,add:rec.status,note:noteId,notes:(await dbGetAll('notes')).length,
     collections:(await dbGetAll('collections')).length};
 },{refs,secret});
 ck('source_synthetic_note_and_collection_created',seededA.add==='ADDED'&&seededA.notes===1&&seededA.collections===1,seededA);
 const diagnostics=await a.evaluate(async data=>{
   await goSearch();
   setSearchQueryDraft(data.q,{mode:'words',syncOther:true});
   recordLocalDiagnostic('R10 synthetic with user-entered private material',new Error(data.secret));
   const copied=await diagnosticsText();
   return {hasNote:copied.includes(data.secret),hasSearch:copied.includes(data.q),
     containsDiagHeader:copied.includes('Livre du Ciel — diagnostic public'),
     hasAppVersion:copied.includes('142.18'),length:copied.length,
     recentErrorNames:copied.includes('Erreur locale'),rawNoteCount:(await dbGetAll('notes')).length};
 },{secret,q:querySentinel});
 ck('public_diagnostic_excludes_synthetic_note_and_search_query',
   !diagnostics.hasNote&&!diagnostics.hasSearch&&diagnostics.containsDiagHeader&&diagnostics.hasAppVersion,
   diagnostics);
 const dataA=await a.evaluate(async()=>{
   const built=await buildUserDataStreamBackup();
   const raw=await new File(built.parts,'R10_VALID.ldcbackup',{type:'application/x-ndjson'}).text();
   return {raw,records:built.totalRecords};
 });
 const exported={records:dataA.records,bytes:Buffer.byteLength(dataA.raw,'utf8'),
   hasNote:dataA.raw.includes(secret),trailerComplete:false};
 try{const tr=JSON.parse(dataA.raw.trimEnd().split('\n').at(-1));exported.trailerComplete=tr.complete===true}catch(_){}
 ck('backup_stream_contains_private_note_and_terminal_integrity',
   exported.records>=3&&exported.hasNote&&exported.trailerComplete,exported);
 const target=await b.evaluate(async data=>{
   const id=await dbPut('collections',{name:'R10 DESTINATION BEFORE RESTORE',ts:Date.now()});
   await dbAddCollectionItemAtomic(id,{...data.refs,note:'DESTINATION_OLD',ts:Date.now()});
   await dbPut('settings',{key:'textLevel',val:'normal',ts:Date.now()});
   return {collection:id,colls:(await dbGetAll('collections')).map(x=>x.name)};
 },{refs});
 ck('destination_initially_separate_from_source',target.colls.length===1&&target.colls[0]==='R10 DESTINATION BEFORE RESTORE',target);
 const adversarial=await b.evaluate(async data=>{
   const orig=data.raw;
   const before=(await dbGetAll('collections')).map(x=>x.name).join('|');
   const cut=orig.slice(0,orig.lastIndexOf('\n',orig.length-2)+1);
   let truncatedRejected=false,truncatedErrorType='';
   try{await parseBackupStreamToStage(new File([cut],'truncated.ldcbackup',{type:'application/x-ndjson'}))}
   catch(e){truncatedRejected=true;truncatedErrorType=/tronqu|marqueur final|CRC/i.test(String(e.message))?'INTEGRITY_OR_TRUNCATION':'OTHER_REJECT';}
   const tampered=orig.replace('R10 SOURCE COLLECTION','R10 SOURXE COLLECTION');
   let tamperedRejected=false,tamperedReason='';
   try{await parseBackupStreamToStage(new File([tampered],'tampered.ldcbackup',{type:'application/x-ndjson'}))}
   catch(e){tamperedRejected=true;tamperedReason=/CRC|intégrité/i.test(String(e.message))?'CRC':'OTHER_REJECT';}
   const after=(await dbGetAll('collections')).map(x=>x.name).join('|');
   return {truncatedRejected,truncatedErrorType,tamperedRejected,tamperedReason,stateUnchanged:before===after};
 },{raw:dataA.raw});
 ck('truncated_stream_rejected_without_state_mutation',
   adversarial.truncatedRejected&&adversarial.stateUnchanged,{rejected:adversarial.truncatedRejected,reason:adversarial.truncatedErrorType,unchanged:adversarial.stateUnchanged});
 ck('modified_stream_CRC_rejected_without_state_mutation',
   adversarial.tamperedRejected&&adversarial.tamperedReason==='CRC'&&adversarial.stateUnchanged,adversarial);
 const prepared=await b.evaluate(async raw=>{
   const file=new File([raw],'R10_VALID.ldcbackup',{type:'application/x-ndjson'});
   const parsed=await parseBackupStreamToStage(file);
   parsed.migrationSummary=await migrateBackupStageToCurrent(parsed);
   const checked=await validateBackupStage(parsed);
   return {token:parsed.token,valid:checked.ok,errors:checked.errors,warnings:checked.warnings,
     counts:checked.counts,migrationSteps:parsed.migrationSummary?.steps||[]};
 },dataA.raw);
 ck('real_restore_staged_migrated_validated',
   prepared.valid===true&&prepared.errors.length===0&&prepared.counts.collections===1&&prepared.counts.notes===1,
   {valid:prepared.valid,errors:prepared.errors,warnings:prepared.warnings,counts:prepared.counts,migrationSteps:prepared.migrationSteps});
 const completed=await b.evaluate(async()=>{
   const meta=await getBackupStageMeta();
   if(!meta||meta.status!=='READY')return {committed:false,metaStatus:meta?.status};
   await atomicSwapBackupStage(meta.token);
   await applyImportedPreferences();
   return {committed:true,collections:(await dbGetAll('collections')).map(x=>x.name),
     notes:(await dbGetAll('notes')).map(x=>({text:x.text,entry_id:x.entry_id})),
     children:(await dbGetAll('col_items')).length,
     textSetting:(await dbGet('settings','textLevel'))?.val,
     stageMeta:await getBackupStageMeta()};
 });
 ck('full_atomic_stream_restore_replaces_fresh_profile_state',
   completed.committed&&completed.collections?.length===1&&completed.collections[0]==='R10 SOURCE COLLECTION'&&
   completed.notes?.length===1&&completed.notes[0].text===secret&&completed.children===1&&
   completed.textSetting==='grand'&&completed.stageMeta==null,
   {committed:completed.committed,collectionNames:completed.collections,noteCount:completed.notes?.length,
    restoredNoteExact:completed.notes?.[0]?.text===secret,childCount:completed.children,
    textSetting:completed.textSetting,stageCleared:completed.stageMeta==null});
 await b.reload({waitUntil:'domcontentloaded',timeout:90000});
 await b.waitForFunction(()=>typeof dbGetAll==='function'&&!!db,null,{timeout:90000});
 const durable=await b.evaluate(async()=>({col:(await dbGetAll('collections')).map(x=>x.name),
   notes:(await dbGetAll('notes')).length,children:(await dbGetAll('col_items')).length,
   textLevel:(await dbGet('settings','textLevel'))?.val}));
 ck('restored_state_survives_browsing_restart',durable.col.length===1&&durable.col[0]==='R10 SOURCE COLLECTION'&&
   durable.notes===1&&durable.children===1&&durable.textLevel==='grand',durable);
 ck('no_unhandled_page_errors',errors.length===0,errors.slice(0,5));
 report.status=Object.values(report.checks).every(Boolean)?'PASS_SCOPED_REAL_BROWSER_RESTORE_AND_PRIVACY':'FAIL';
} catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_R10_BACKUP_FULL_RESTORE_AND_DIAG_PRIVACY_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,checks:report.checks,errors:report.errors},null,2));
 if(browser)await browser.close().catch(()=>{});if(server)server.kill('SIGTERM');
 if(report.status!=='PASS_SCOPED_REAL_BROWSER_RESTORE_AND_PRIVACY')process.exitCode=1;
}
