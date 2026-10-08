import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const dir=process.env.LDC_ARCHIVE_EXTRACT_DIR,port=8999,url='http://127.0.0.1:'+port+'/';
const report={schema:'ldc-v14218-r10-large-backup-atomic-abort-qa-v1',source:'7c292d6221bb350fac3aeaa83750b8784706d45c',zip_sha256:'954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb',
  status:'NOT_RUN',checks:{},details:{},errors:[],scope:'Synthetic-only 750 notes in two fresh Chromium browser profiles; no physical or hosted test',
  no_app_mutation:true,deployment_authority:'NONE',physical_iOS:'OPEN',hosted_E16_E19:'OPEN'};
const ck=(k,ok,x)=>{report.checks[k]=!!ok;if(x!==undefined)report.details[k]=x};
let browser,server;
try{
 if(!dir||!fs.existsSync(dir+'/PACKAGE_MANIFEST_SHA256.json'))throw Error('MISSING_EXACT_APP_ARCHIVE');
 const m=JSON.parse(fs.readFileSync(dir+'/PACKAGE_MANIFEST_SHA256.json','utf8'));
 ck('frozen_273_resource_manifest',m.source_commit===report.source&&m.files.length===273);
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',dir],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
 const a=await browser.newContext({serviceWorkers:'allow'}),b=await browser.newContext({serviceWorkers:'allow'});
 const p=await a.newPage(),q=await b.newPage(),errs=[];for(const x of [p,q]){x.setDefaultTimeout(180000);x.on('pageerror',e=>errs.push(String(e)))}
 for(const x of [p,q]){await x.goto(url,{waitUntil:'domcontentloaded',timeout:120000});await x.waitForFunction(()=>typeof buildUserDataStreamBackup==='function'&&!!db,null,{timeout:120000})}
 const refs={volume:1,entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001'};
 const t0=Date.now();
 const seeded=await p.evaluate(async ref=>new Promise((resolve,reject)=>{
  const tx=db.transaction('notes','readwrite'),st=tx.objectStore('notes');let seeded=0;
  for(let i=0;i<750;i++){
    const row={...ref,ts:Date.now()+i,text:'R10_SYNTHETIC_NOTE_'+i.toString().padStart(4,'0')+' '+('abcde'.repeat(40)),quote:'synth'};
    const request=st.add(row);request.onsuccess=()=>seeded++;request.onerror=()=>reject(request.error);
  }
  tx.oncomplete=()=>resolve({count:seeded});tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);
 }),refs);
 ck('750_synthetic_user_notes_created',seeded.count===750,seeded);
 const data=await p.evaluate(async()=>{
  const r=await buildUserDataStreamBackup();
  const raw=await new File(r.parts,'stress.ldcbackup',{type:'application/x-ndjson'}).text();
  return {raw,bytes:new Blob(r.parts).size,records:r.totalRecords,parts:r.parts.length};
 });
 ck('multi_chunk_stress_backup_stream_created',data.records>=750&&data.bytes>100000&&data.parts.length>=1,
  {records:data.records,bytes:data.bytes,parts:data.parts.length});
 const original=await q.evaluate(async()=>{
  const id=await dbPut('collections',{name:'DO_NOT_LOSE_PRIOR_TARGET',ts:Date.now()});
  return {id,previous:(await dbGetAll('collections')).length};
 });
 const prep=await q.evaluate(async raw=>{
  const p=await parseBackupStreamToStage(new File([raw],'stress.ldcbackup',{type:'application/x-ndjson'}));
  p.migrationSummary=await migrateBackupStageToCurrent(p);
  const v=await validateBackupStage(p);
  return {valid:v.ok,notes:v.counts.notes,errors:v.errors,warnings:v.warnings};
 },data.raw);
 ck('750_note_backup_staged_and_validated',prep.valid&&prep.notes===750&&prep.errors.length===0,
  {valid:prep.valid,notes:prep.notes,errors:prep.errors?.slice(0,2),warnings:prep.warnings?.slice(0,2)});
 const swapped=await q.evaluate(async()=>{
  const meta=await getBackupStageMeta();if(!meta||meta.status!=='READY')return {committed:false};
  await atomicSwapBackupStage(meta.token);
  return {committed:true,notes:(await dbGetAll('notes')).length,oldCollections:(await dbGetAll('collections')).filter(x=>x.name==='DO_NOT_LOSE_PRIOR_TARGET').length};
 });
 ck('real_750_note_atomic_replacement_in_fresh_profile',swapped.committed&&swapped.notes===750&&swapped.oldCollections===0,swapped);
 await q.reload({waitUntil:'domcontentloaded',timeout:120000});
 await q.waitForFunction(()=>typeof dbGetAll==='function'&&!!db,null,{timeout:120000});
 const durable=await q.evaluate(async()=>{
  const notes=await dbGetAll('notes');return {n:notes.length,first:notes[0]?.text?.startsWith('R10_SYNTHETIC_NOTE_0000'),
    last:notes.at(-1)?.text?.startsWith('R10_SYNTHETIC_NOTE_0749')};
 });
 ck('750_note_restore_persists_after_reopen',durable.n===750&&durable.first&&durable.last,durable);
 const hold=await q.evaluate(async()=>{
   const id=await dbPut('collections',{name:'R10_ROLLBACK_SENTINEL',ts:Date.now()});
   const before={collection:(await dbGetAll('collections')).map(x=>x.name),notes:(await dbGetAll('notes')).length};
   const built=await buildUserDataStreamBackup();
   const file=new File(built.parts,'rollback.ldcbackup',{type:'application/x-ndjson'});
   const parsed=await parseBackupStreamToStage(file);
   const validated=await validateBackupStage(parsed);
   if(!validated.ok)throw new Error('PRECONDITION_INVALID_STAGE');
   // Controlled fault injection directly in disposable staging DB only AFTER normal validation:
   // a row with a non-IndexedDB primary key forces .put(DataError), and the whole
   // canonical transaction must roll back without losing prior user records.
   const tx=db.transaction(USER_DATA_STAGE_STORE,'readwrite');
   await new Promise((resolve,reject)=>{
     const s=tx.objectStore(USER_DATA_STAGE_STORE);
     const bad=s.put({stage_key:['notes',999999],token:parsed.token,store:'notes',
       row:{id:{INVALID_IDB_KEY:true},entry_id:'ldc_t01_editorial_explications_note001',text:'invalid'}});
     bad.onerror=()=>reject(bad.error);
     tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);
   });
   let rejected=false,reason='';
   try{await atomicSwapBackupStage(parsed.token)}catch(e){rejected=true;reason=String(e?.name||e?.message||e).slice(0,120)}
   const after={collection:(await dbGetAll('collections')).map(x=>x.name),notes:(await dbGetAll('notes')).length};
   await clearBackupStage();
   return {rejected,reason,unchanged:JSON.stringify(before)===JSON.stringify(after),before,after};
 });
 ck('injected_invalid_staged_key_aborts_entire_atomic_import_without_data_loss',
   hold.rejected&&hold.unchanged&&hold.after.notes===750&&hold.after.collection.includes('R10_ROLLBACK_SENTINEL'),
   hold);
 ck('no_unhandled_browser_page_errors',errs.length===0,errs.slice(0,3));
 report.details.total_elapsed_seconds=Math.round((Date.now()-t0)/1000);
 report.status=Object.values(report.checks).every(Boolean)?'PASS_SCOPED_750_NOTE_RESTORE_AND_FAULT_ROLLBACK':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync('LDC_v142.18_R10_LARGE_BACKUP_FAULT_ABORT_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,checks:report.checks,errors:report.errors},null,2));
 if(browser)await browser.close().catch(()=>{});if(server)server.kill('SIGTERM');
 if(report.status!=='PASS_SCOPED_750_NOTE_RESTORE_AND_FAULT_ROLLBACK')process.exitCode=1;
}