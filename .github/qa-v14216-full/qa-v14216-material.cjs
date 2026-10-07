const {chromium}=require('playwright'),fs=require('fs');
const URL='http://127.0.0.1:8315/';
const out={overall:'UNKNOWN',checks:{},details:{},errors:[]};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function ck(k,v,d){out.checks[k]=!!v;if(d!==undefined)out.details[k]=d;}
(async()=>{
 const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:820,height:1180},serviceWorkers:'allow',locale:'fr-FR'});const p=await c.newPage();p.on('pageerror',e=>out.errors.push('page:'+e));
 try{
  await p.goto(URL,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForFunction(()=>{const l=document.getElementById('loading');return l&&getComputedStyle(l).display==='none'&&typeof APP_VERSION==='string';},null,{timeout:120000});
  await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none'&&typeof finishOnboarding==='function')finishOnboarding();});
  const ids=await p.evaluate(()=>({app:APP_VERSION,pub:PUBLIC_VERSION,sw:SW_CACHE_VERSION}));ck('identity',ids.app==='v2.19.142.16-R1B-RELEASE-INTEGRITY-CLOSURE'&&ids.pub==='142.16',ids);
  // all 36 volume routes and first-reader path
  const vols=await p.evaluate(async()=>{const r=[];await goTomes();for(let v=1;v<=36;v++){await openTome(v);const n=document.querySelectorAll('#entries-list .entry-item').length;r.push({v,n});}return r;});
  ck('all_36_tomes_open',vols.length===36&&vols.every(x=>x.n>0),vols);
  await p.evaluate(async()=>{await openTome(1);document.querySelector('#entries-list .entry-item')?.click();});
  await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active')&&document.querySelector('#reader-body .para-fragment'),null,{timeout:90000});
  const base=await p.evaluate(()=>({entry:currentEntry?.id,pid:document.querySelector('#reader-body .para-fragment')?.dataset.paraId,paras:document.querySelectorAll('#reader-body .para-fragment').length}));
  ck('reader_first_entry',!!base.entry&&!!base.pid&&base.paras>0,base);
  // favorite
  await p.click('#reader-fav-top');await sleep(150);const fav=await p.evaluate(id=>dbGet('favorites',id),base.entry);ck('favorite_persist_write',!!fav,fav);
  // note
  const note=await p.evaluate(async pid=>{showParagraphContext(pid);contextNote();document.getElementById('note-input').value='FULLQA_NOTE_14216';await saveNote();return (await dbGetAll('notes')).find(x=>x.text==='FULLQA_NOTE_14216')||null;},base.pid);ck('note_write',!!note,note&&{id:note.id,para:note.para_id});
  // highlight using actual context/picker flow
  const hl=await p.evaluate(async pid=>{showParagraphContext(pid);contextHighlight();await pickHighlight('yellow');const all=await dbGetAll('highlights');return {count:all.length,row:all[0]||null,marks:document.querySelectorAll('#reader-body mark.hl').length};},base.pid);ck('highlight_write_render',hl.count>0&&hl.marks>0,hl);
  // collection using actual context + create flow
  const col=await p.evaluate(async pid=>{showParagraphContext(pid);contextCollection();document.getElementById('col-new-input').value='FULLQA_COLLECTION_14216';await createAndAddCollection();return {cols:await dbGetAll('collections'),items:await dbGetAll('col_items')};},base.pid);ck('collection_create_add',col.cols.some(x=>x.name==='FULLQA_COLLECTION_14216')&&col.items.length>0,{cols:col.cols.length,items:col.items.length});
  // date navigation
  const dn=await p.evaluate(async()=>{await openDateNav();return {screen:document.querySelector('.screen.active')?.id,years:document.querySelectorAll('.dn-year-pill').length,months:document.querySelectorAll('.dn-month-cell').length,days:document.querySelectorAll('.dn-day-cell').length};});ck('date_navigation',dn.screen==='screen-date-nav'&&dn.years>0&&dn.months>0,dn);
  // help
  const help=await p.evaluate(async()=>{await openHelp();return {screen:document.querySelector('.screen.active')?.id,text:document.querySelector('#screen-help')?.innerText?.slice(0,200)||''};});ck('help_open',help.screen==='screen-help'&&help.text.length>50,help);
  // preferences
  await p.evaluate(async()=>{await setThemePreference('dark');await setTextLevel('large');const cur=await dbGet('settings','showReperes');if(!(cur&&cur.val===true))await toggleReperes();});
  await p.reload({waitUntil:'domcontentloaded',timeout:120000});await p.waitForFunction(()=>{const l=document.getElementById('loading');return l&&getComputedStyle(l).display==='none';},null,{timeout:120000});
  const prefs=await p.evaluate(async()=>({theme:document.documentElement.getAttribute('data-theme'),text:document.documentElement.getAttribute('data-text-level'),rep:!!(await dbGet('settings','showReperes'))?.val,fav:!!(await dbGet('favorites',"ldc_t01_sec001")),notes:(await dbGetAll('notes')).length,hl:(await dbGetAll('highlights')).length,cols:(await dbGetAll('collections')).length,items:(await dbGetAll('col_items')).length}));
  ck('preferences_reopen',prefs.theme==='dark'&&prefs.text==='large'&&prefs.rep,prefs);
  ck('user_data_reopen',prefs.fav&&prefs.notes>0&&prefs.hl>0&&prefs.cols>0&&prefs.items>0,prefs);
  // streaming backup + real staged restore roundtrip
  const backup=await p.evaluate(async()=>{
    const built=await buildUserDataStreamBackup();
    const file=new File(built.parts,'fullqa.ldcbackup',{type:USER_DATA_STREAM_MIME});
    await dbPut('settings',{key:'FULLQA_AFTER_BACKUP',val:'must_disappear',ts:Date.now()});
    let parsed=await parseBackupStreamToStage(file);
    parsed.migrationSummary=await migrateBackupStageToCurrent(parsed);
    const validation=await validateBackupStage(parsed);
    pendingBackupImport={kind:'stream',token:parsed.token,validation,fileName:file.name,header:parsed.header,migrationSummary:parsed.migrationSummary};
    await confirmImportBackupStream();
    return {records:built.totalRecords,crc:built.crc32,validation,after:await dbGet('settings','FULLQA_AFTER_BACKUP'),notes:(await dbGetAll('notes')).length,hl:(await dbGetAll('highlights')).length,favs:(await dbGetAll('favorites')).length,cols:(await dbGetAll('collections')).length,items:(await dbGetAll('col_items')).length};
  });
  ck('backup_restore_roundtrip',backup.records>0&&backup.validation.ok===true&&!backup.after&&backup.notes>0&&backup.hl>0&&backup.favs>0&&backup.cols>0&&backup.items>0,backup);
  // Mon Espace material tabs
  const esp=await p.evaluate(async()=>{await goEspace();const r={};for(const t of ['notes','highlights','favorites','collections']){showEspaceTab(t);r[t]={selected:document.getElementById('es-tab-'+t)?.getAttribute('aria-selected'),text:document.getElementById('ep-'+t)?.innerText?.slice(0,120)||''};}return r;});
  ck('espace_tabs',Object.values(esp).every(x=>x.selected==='true'&&x.text.length>0),esp);
  // invalid deep link parser fails closed
  const deep=await p.evaluate(()=>({bad1:parseDeepLinkUrl(location.origin+location.pathname+'?view=entry&tome=999&entry=x'),bad2:parseDeepLinkUrl(location.origin+location.pathname+'?view=collection&collection=-1')}));
  ck('invalid_deep_links_rejected',deep.bad1?.ok===false&&deep.bad2?.ok===false,deep);
  out.overall=Object.values(out.checks).every(Boolean)&&out.errors.length===0?'PASS':'FAIL';
 }catch(e){out.errors.push(String(e&&e.stack||e));out.overall='HARNESS_OR_APP_FAILURE';}
 await c.close();await b.close();fs.writeFileSync('qa-v14216-material-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));if(out.overall!=='PASS')process.exitCode=1;
})().catch(e=>{out.errors.push(String(e&&e.stack||e));out.overall='HARNESS_ERROR';fs.writeFileSync('qa-v14216-material-results.json',JSON.stringify(out,null,2)+'\n');console.error(e);process.exitCode=2;});
