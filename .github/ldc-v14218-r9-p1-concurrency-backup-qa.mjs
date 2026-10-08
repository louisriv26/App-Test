import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const port=8988,base='http://127.0.0.1:'+port+'/',dir=process.env.LDC_ARCHIVE_EXTRACT_DIR;
const report={schema:'ldc-v14218-r9-cross-tab-transaction-and-stream-backup-browser-v2-valid-paragraph-fixtures',
 exact_zip_sha256:'954085cc54cbc401d49512811276b5c633c72b9f48e8963881792f176b20d7eb',
 exact_source_commit:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 status:'NOT_RUN',checks:{},details:{},errors:[],
 scope:'Fresh, disposable local Chromium origin only. Full actual frozen ZIP. No live app or device.',
 hosted_e16_e19:'OPEN',physical_gate:'OPEN',no_application_mutation:true,deploy_authority:'NONE'};
const ck=(name,ok,data)=>{report.checks[name]=!!ok;if(data!==undefined)report.details[name]=data};
let server,browser;
try{
 if(!dir||!fs.existsSync(dir+'/PACKAGE_MANIFEST_SHA256.json'))throw Error('ARCHIVE_NOT_EXTRACTED');
 server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',dir],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,900));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({serviceWorkers:'allow'}),a=await ctx.newPage(),b=await ctx.newPage();
 const pageErrors=[];for(const p of [a,b]){p.on('pageerror',e=>pageErrors.push(String(e)));p.setDefaultTimeout(180000)}
 async function boot(p){await p.goto(base,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForFunction(()=>typeof dbSaveCollectionItemNoteAtomic==='function'&&!!db&&typeof buildUserDataStreamBackup==='function',null,{timeout:120000});}
 await boot(a);await boot(b);
 const dbs=await Promise.all([a,b].map(p=>p.evaluate(()=>({public:PUBLIC_VERSION,dbName:DB_NAME,stores:USER_DATA_STORES.slice()}))));
 ck('exact_archive_source_and_same_origin_fresh_multi_tab',dbs.every(x=>x.public==='142.18'&&x.dbName==='ldc_user_v1'&&x.stores.includes('col_items')),dbs);
 const ids=await a.evaluate(async()=>{
  const id=await dbPut('collections',{name:'R9 synthetic fixture',ts:Date.now()});
  const x=await dbAddCollectionItemAtomic(id,{entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',volume:1,stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001',note:'base',ts:Date.now()});
  const y=await dbAddCollectionItemAtomic(id,{entry_id:'ldc_t01_editorial_explications_note002',para_id:'ldc_t01_editorial_explications_note002_p001',volume:1,stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE002.P001',note:'note 2',ts:Date.now()});
  return {col:id,first:x,second:y};
 });
 ck('atomic_parent_and_two_children_created',ids.first.status==='ADDED'&&ids.second.status==='ADDED'&&ids.first.record.col_id===ids.col,ids);
 const idA=ids.first.record.id,idB=ids.second.record.id,col=ids.col;
 const fresh=await b.evaluate(async v=>dbSaveCollectionItemNoteAtomic(v.id,'base','fresh-edit-B'),{id:idA});
 const stale=await a.evaluate(async v=>dbSaveCollectionItemNoteAtomic(v.id,'base','stale-edit-A'),{id:idA});
 const durable=await a.evaluate(async id=>dbGet('col_items',id),idA);
 ck('cross_tab_stale_note_edit_rejected_without_overwriting_fresh',fresh.status==='UPDATED'&&stale.status==='CONFLICT'&&durable.note==='fresh-edit-B',{fresh:fresh.status,stale:stale.status,note:durable.note});
 const renameFresh=await b.evaluate(async col=>dbRenameCollectionAtomic(col,'R9 synthetic fixture','R9 fresh B'),col);
 const renameStale=await a.evaluate(async col=>dbRenameCollectionAtomic(col,'R9 synthetic fixture','R9 stale A'),col);
 const actualCol=await a.evaluate(async col=>dbGet('collections',col),col);
 ck('cross_tab_stale_collection_rename_rejected',renameFresh.status==='UPDATED'&&renameStale.status==='CONFLICT'&&actualCol.name==='R9 fresh B',{fresh:renameFresh.status,stale:renameStale.status,name:actualCol.name});
 const addThird=await b.evaluate(async col=>dbAddCollectionItemAtomic(col,{entry_id:'ldc_t01_editorial_explications_note003',para_id:'ldc_t01_editorial_explications_note003_p001',volume:1,stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE003.P001',note:'third'}),col);
 const staleDrag=await a.evaluate(async v=>dbReorderCollectionAtomic(v.col,{kind:'drag',ids:v.ids}),{col,ids:[idB,idA]});
 const afterDrag=await a.evaluate(async col=>(await dbGetAll('col_items')).filter(r=>r.col_id===col).sort((x,y)=>x.order-y.order).map(x=>({id:x.id,order:x.order})),col);
 ck('stale_drag_does_not_drop_newly_added_item',addThird.status==='ADDED'&&staleDrag.status==='MEMBERSHIP_CHANGED'&&afterDrag.length===3&&afterDrag.every((x,i)=>x.order===i+1),{add:addThird.status,drag:staleDrag.status,rows:afterDrag});
 const move=await a.evaluate(async v=>dbReorderCollectionAtomic(v.col,{kind:'move',itemId:v.id,dir:1}),{col,id:idA});
 const afterMove=await b.evaluate(async col=>(await dbGetAll('col_items')).filter(r=>r.col_id===col).sort((x,y)=>x.order-y.order).map(x=>({id:x.id,order:x.order})),col);
 ck('fresh_transactional_reorder_consistent',move.status==='UPDATED'&&afterMove.length===3&&afterMove.every((x,i)=>x.order===i+1),{status:move.status,rows:afterMove});
 const deleted=await b.evaluate(async col=>dbDeleteCollectionAtomic(col),col);
 const orphan=await a.evaluate(async col=>dbAddCollectionItemAtomic(col,{entry_id:'R9_ORPHAN',note:'must_not_commit'}),col);
 const surviving=await a.evaluate(async col=>({parent:await dbGet('collections',col),children:(await dbGetAll('col_items')).filter(r=>r.col_id===col)}),col);
 ck('atomic_parent_deletion_and_orphan_guard',deleted.status==='DELETED'&&deleted.deletedItems===3&&orphan.status==='PARENT_MISSING'&&!surviving.parent&&surviving.children.length===0,{delete:deleted.status,childCount:deleted.deletedItems,orphan:orphan.status});
 const malformed=await a.evaluate(async data=>dbRestoreCollectionAtomic({id:data.col,name:'fake'},[{id:987654321,col_id:data.col+99}]),{col});
 ck('malformed_undo_snapshot_rejected',malformed.status==='INVALID_SNAPSHOT',malformed);
 const restored=await a.evaluate(async snap=>dbRestoreCollectionAtomic(snap.parent,snap.children),{parent:deleted.parent,children:deleted.children});
 const restoredChildren=await b.evaluate(async col=>(await dbGetAll('col_items')).filter(r=>r.col_id===col),col);
 ck('complete_atomic_collection_undo_restores_children',restored.status==='RESTORED'&&restoredChildren.length===3&&restoredChildren.some(x=>x.id===idA&&x.note==='fresh-edit-B'),{result:restored.status,children:restoredChildren.length,note:restoredChildren.find(x=>x.id===idA)?.note});
 const backup=await a.evaluate(async()=>{
  const output=await buildUserDataStreamBackup();
  const file=new File(output.parts,'R9_SYNTHETIC.ldcbackup',{type:'application/x-ndjson'});
  const header=await file.text();
  const tr=header.trim().split('\n').at(-1);
  return {parts:output.parts.length,size:file.size,records:output.totalRecords,header:header.slice(0,160),tail:tr.slice(0,180),goodTrailer:JSON.parse(tr).complete===true};
 });
 ck('canonical_streaming_backup_contains_records_and_terminal_crc',backup.goodTrailer&&backup.records>=4&&backup.size>500,backup);
 const stage=await a.evaluate(async()=>{
  const built=await buildUserDataStreamBackup();
  const file=new File(built.parts,'R9_SYNTHETIC.ldcbackup',{type:'application/x-ndjson'});
  const parsed=await parseBackupStreamToStage(file);
  const validated=await validateBackupStage(parsed);
  const keys={status:parsed.status,errors:validated.errors?.slice(0,5),warnings:validated.warnings?.slice(0,5),valid:validated.ok,
   parsed_counts:parsed.counts,records:built.totalRecords};
  await clearBackupStage();
  return keys;
 });
 ck('normal_streaming_backup_stage_validation_succeeds_without_commit',stage.valid===true||stage.errors?.length===0,stage);
 const afterward=await a.evaluate(async v=>({item:await dbGet('col_items',v.id),parent:await dbGet('collections',v.col)}),{id:idA,col});
 ck('backup_validation_does_not_mutate_current_personal_state',afterward.item?.note==='fresh-edit-B'&&afterward.parent?.name==='R9 fresh B',afterward);
 ck('no_unhandled_browser_page_errors',pageErrors.length===0,pageErrors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS_SCOPED_REAL_BROWSER_P1_INTEGRITY_ONLY':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e))}
finally{
 fs.writeFileSync('LDC_v142.18_R9_MULTI_TAB_BACKUP_INTEGRITY_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS_SCOPED_REAL_BROWSER_P1_INTEGRITY_ONLY')process.exitCode=1;
}
