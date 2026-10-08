import fs from 'node:fs';
import cp from 'node:child_process';
import { chromium } from 'playwright-core';
const dir=process.env.LDC_ARCHIVE_EXTRACT_DIR,url='http://127.0.0.1:8997/';
const out={schema:'ldc-v14218-r11-dirty-draft-update-and-beforeunload-browser-qa-v1',
app_source:'7c292d6221bb350fac3aeaa83750b8784706d45c',
app_zip_sha256:'954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb',
status:'NOT_RUN',checks:{},details:{},errors:[],scope:'Exact immutable ZIP, local Chromium only. No update published, no real user data touched.',
deploy_authority:'NONE',app_mutation_authority:'NONE',hosted_gate:'OPEN',physical_gate:'OPEN'};
const check=(name,pass,detail)=>{out.checks[name]=!!pass;if(detail!==undefined)out.details[name]=detail};
let browser,server;
try{
 const manifest=JSON.parse(fs.readFileSync(dir+'/PACKAGE_MANIFEST_SHA256.json','utf8'));
 check('exact_frozen_package_manifest',manifest.files.length===273&&manifest.source_commit===out.app_source);
 server=cp.spawn('python3',['-m','http.server','8997','--bind','127.0.0.1','--directory',dir],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({serviceWorkers:'allow'}),page=await ctx.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(90000);
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>!!db&&typeof reloadForUpdate==='function'&&typeof ldcUnsafeReloadState==='function',null,{timeout:90000});
 const control=await page.evaluate(()=>({
  before:ldcUnsafeReloadState(),version:PUBLIC_VERSION,
  draft:document.getElementById('note-input')?.value,
  banner:document.getElementById('update-banner')?.className
 }));
 check('clean_start_update_safe_and_public_version',!control.before.unsafe&&control.version==='142.18',control);
 // Real markup but synthetic draft: do not save or commit.
 const note=await page.evaluate(async()=>{
  const el=document.getElementById('note-overlay');el.classList.add('show');
  const field=document.getElementById('note-input');field.value='R11 synthetic unsaved note';
  const before=ldcUnsafeReloadState(),decision=await reloadForUpdate();
  const status=document.getElementById('update-check-status')?.innerText||'';
  return {before,decision,status};
 });
 check('unsaved_note_blocks_update_before_SW_interaction',note.before.reasons.includes('note')&&note.decision.status==='BLOCKED'&&note.decision.reasons.includes('note')&&/différée/i.test(note.status),note);
 const noteCancelled=await page.evaluate(()=>{
  document.getElementById('note-overlay').classList.remove('show');document.getElementById('note-input').value='';
  return ldcUnsafeReloadState()
 });
 check('cancelled_note_removes_block_without_data_write',!noteCancelled.unsafe,noteCancelled);
 const collection=await page.evaluate(async()=>{
  document.getElementById('col-overlay').classList.add('show');
  document.getElementById('col-new-input').value='R11 synthetic unsaved collection';
  const blocked=await reloadForUpdate();
  document.getElementById('col-overlay').classList.remove('show');
  document.getElementById('col-new-input').value='';
  return blocked;
 });
 check('unsaved_collection_name_blocks_reload',collection.status==='BLOCKED'&&collection.reasons.includes('new_collection'),collection);
 const collectionNote=await page.evaluate(async()=>{
  const textarea=document.createElement('textarea');textarea.className='ci-note-edit show';textarea.value='new unsaved';textarea.dataset.baseNote='old';
  document.body.appendChild(textarea);
  const blocked=await reloadForUpdate();textarea.remove();
  return blocked;
 });
 check('unsaved_collection_item_note_blocks_reload',collectionNote.status==='BLOCKED'&&collectionNote.reasons.includes('collection_note'),collectionNote);
 const issue=await page.evaluate(async()=>{
  document.getElementById('report-issue-overlay').classList.add('show');
  document.getElementById('report-issue-comment').value='R11 synthetic unsaved report';
  const blocked=await reloadForUpdate();
  document.getElementById('report-issue-overlay').classList.remove('show');
  document.getElementById('report-issue-comment').value='';
  return blocked;
 });
 check('unsaved_documentary_report_blocks_reload',issue.status==='BLOCKED'&&issue.reasons.includes('issue_comment'),issue);
 const preview=await page.evaluate(async()=>{
  pendingBackupImport={kind:'stream',token:'R11_TEST_ONLY_DO_NOT_COMMIT'};
  const blocked=await reloadForUpdate();pendingBackupImport=null;
  return blocked;
 });
 check('pending_backup_preview_blocks_reload',preview.status==='BLOCKED'&&preview.reasons.includes('backup_preview'),preview);
 const busy=await page.evaluate(async()=>{
  backupImportBusy=true;const blocked=await reloadForUpdate();backupImportBusy=false;return blocked;
 });
 check('backup_import_in_progress_blocks_reload',busy.status==='BLOCKED'&&busy.reasons.includes('backup_busy'),busy);
 const clear=await page.evaluate(async()=>({state:ldcUnsafeReloadState(),notes:(await dbGetAll('notes')).length,collections:(await dbGetAll('collections')).length}));
 check('synthetic_drafts_did_not_modify_personal_database',!clear.state.unsafe&&clear.notes===0&&clear.collections===0,clear);
 check('no_unexpected_page_errors',errors.length===0,errors);
 out.status=Object.values(out.checks).every(Boolean)?'PASS_SCOPED_UPDATE_DRAFT_SAFETY_NO_DEPLOY':'FAIL';
}catch(e){out.status='FAIL';out.errors.push(String(e?.stack||e))}
finally{
 fs.writeFileSync('LDC_v142.18_R11_UPDATE_DRAFT_SAFETY_QA.json',JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2));
 if(browser)await browser.close().catch(()=>{});if(server)server.kill('SIGTERM');
 if(out.status!=='PASS_SCOPED_UPDATE_DRAFT_SAFETY_NO_DEPLOY')process.exitCode=1;
}