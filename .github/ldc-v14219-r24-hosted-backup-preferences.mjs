import fs from 'node:fs';
import {chromium} from 'playwright';
const URL='https://louisriv26.github.io/mauritius-mass-finder-beta/';
const FILE='LDC_v142.19_R24_HOSTED_BACKUP_PREFERENCES_AND_RECOVERY.json';
const out={schema:'ldc-v14219-r24-new-real-hosted-synthetic-personal-data-and-backup-tests',created:new Date().toISOString(),status:'NOT_RUN',hosted:URL,checks:{},observations:{},errors:[],owner_data_access:'NONE',app_mutation:'NONE'};
const ck=(n,v,d)=>{out.checks[n]=!!v;if(d!==undefined)out.observations[n]=d};
let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow',reducedMotion:'reduce'});
 const page=await ctx.newPage(),jsErrors=[];page.on('pageerror',e=>jsErrors.push(String(e)));page.setDefaultTimeout(165000);
 await page.goto(URL,{waitUntil:'domcontentloaded',timeout:135000});
 await page.waitForFunction(()=>{const el=document.getElementById('loading');return el&&getComputedStyle(el).display==='none'},null,{timeout:145000});
 await page.evaluate(()=>{const ob=document.getElementById('onboarding-overlay');if(ob&&getComputedStyle(ob).display!=='none')finishOnboarding()});
 ck('v14219_exact_hosted_version',(await page.evaluate(()=>PUBLIC_VERSION))==='142.19');
 const theming=[];
 for(const theme of ['dark','light','system']){
  const d=await page.evaluate(async val=>{await setThemePreference(val);return{theme:document.documentElement.dataset.theme,stored:(await dbGet('settings','theme'))?.val}},theme);
  theming.push({target:theme,...d});
 }
 ck('three_real_theme_controls_persist_immediately',theming.every(x=>x.target===x.theme&&x.theme===x.stored),theming);
 const typography=[];
 for(const level of ['small','normal','large','xlarge']){
  const x=await page.evaluate(async val=>{await setTextLevel(val);return{saved:(await dbGet('settings','textLevel'))?.val,active:typeof currentTextLevel!=='undefined'?currentTextLevel:null}},level);
  typography.push({target:level,...x});
 }
 ck('four_real_text_size_settings_persist_immediately',typography.every(x=>x.saved===x.target),typography);
 await page.evaluate(async()=>{await setTextLevel('large');await setThemePreference('dark');await dbPut('settings',{key:'__R24_HOSTED_DISPOSABLE',val:'R24_ONLY'});await dbPut('notes',{entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p001',stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P001',volume:1,text:'R24 synthetic disposable note; not owner data',ts:Date.now()})});
 const record=await page.evaluate(async()=>{
  const pkg=await buildUserDataStreamBackup();
  const file=new File(pkg.parts,'r24.ldcbackup',{type:USER_DATA_STREAM_MIME});
  const text=await file.text(),lines=text.trim().split('\n');
  return{bytes:file.size,totalLines:lines.length,header:JSON.parse(lines[0]),trailer:JSON.parse(lines[lines.length-1]),text};
 });
 ck('normal_backup_complete_header_trailer',record.totalLines>=3&&record.header.type==='header'&&record.trailer.type==='trailer'&&record.trailer.complete===true,{bytes:record.bytes,lines:record.totalLines,header:record.header,trailer:record.trailer});
 const orig=record.text;
 const valid=await page.evaluate(async text=>{
  const file=new File([text],'r24-valid.ldcbackup',{type:USER_DATA_STREAM_MIME});
  const p=await parseBackupStreamToStage(file),v=await validateBackupStage(p);
  return{valid:v.ok,errors:v.errors,counts:p.counts,notes:(await dbGetAll('notes')).map(x=>x.text)}
 },orig);
 ck('backup_parser_and_staging_accepts_real_export_without_changing_live_notes',valid.valid&&valid.notes.some(x=>x.startsWith('R24 synthetic')),valid);
 const invalid=await page.evaluate(async text=>{
  const file=new File([text.slice(0,Math.max(5,text.length-29))],'r24-truncated.ldcbackup',{type:USER_DATA_STREAM_MIME});
  try{await parseBackupStreamToStage(file);return{rejected:false}}
  catch(e){return{rejected:true,message:String(e.message||e),notes:(await dbGetAll('notes')).map(x=>x.text)}}
 },orig);
 ck('truncated_backup_fails_closed_preserving_existing_notes',invalid.rejected&&invalid.notes?.some(x=>x.startsWith('R24 synthetic')),invalid);
 const roundtrip=await page.evaluate(async text=>{
  const p=await parseBackupStreamToStage(new File([text],'r24-valid.ldcbackup',{type:USER_DATA_STREAM_MIME}));
  const valid=await validateBackupStage(p);
  if(!valid.ok)return{valid:false,errors:valid.errors};
  await dbPut('notes',{entry_id:'ldc_t01_editorial_explications_note001',para_id:'ldc_t01_editorial_explications_note001_p002',stable_ref:'LDC.T01.EDITORIAL.EXPLICATIONS.NOTE001.P002',volume:1,text:'R24 AFTER EXPORT EXTRA NOTE',ts:Date.now()});
  const before=(await dbGetAll('notes')).map(x=>x.text);
  await atomicSwapBackupStage(p.token);
  const after=(await dbGetAll('notes')).map(x=>x.text);
  return{valid:true,before,after}
 },orig);
 ck('atomic_backup_import_restores_exact_prior_note_set',roundtrip.valid&&roundtrip.before.includes('R24 AFTER EXPORT EXTRA NOTE')&&!roundtrip.after.includes('R24 AFTER EXPORT EXTRA NOTE')&&roundtrip.after.some(x=>x.startsWith('R24 synthetic')),roundtrip);
 await page.reload({waitUntil:'domcontentloaded',timeout:130000});
 await page.waitForFunction(()=>{const l=document.getElementById('loading');return l&&getComputedStyle(l).display==='none'},null,{timeout:130000});
 const persisted=await page.evaluate(async()=>({app:PUBLIC_VERSION,theme:document.documentElement.dataset.theme,textLevel:(await dbGet('settings','textLevel'))?.val,notes:(await dbGetAll('notes')).map(x=>x.text),extra:(await dbGet('settings','__R24_HOSTED_DISPOSABLE'))?.val}));
 ck('hosted_reboot_retains_theme_size_user_notes_and_synthetic_marker',persisted.app==='142.19'&&persisted.theme==='dark'&&persisted.textLevel==='large'&&persisted.notes.some(x=>x.startsWith('R24 synthetic'))&&persisted.extra==='R24_ONLY',persisted);
 ck('no_unhandled_errors_in_backup_and_settings',jsErrors.length===0,jsErrors);
 await ctx.close();
 out.status=Object.values(out.checks).every(Boolean)?'PASS_SCOPED_HOSTED_R24':'FAIL_SCOPED_R24';
}catch(e){out.errors.push(String(e?.stack||e));out.status='FAIL_OR_HARNESS_INCOMPLETE_R24'}
finally{fs.writeFileSync(FILE,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2));if(browser)await browser.close().catch(()=>{})}
