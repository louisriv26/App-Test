import fs from 'node:fs';import {chromium} from 'playwright';
const URL='https://louisriv26.github.io/mauritius-mass-finder-beta/',ART='LDC_v142.19_R25_HOSTED_INTERRUPTED_OFFLINE_UI_QA.json';
const out={schema:'ldc-v14219-r25-live-hosted-interrupted-offline-preparation-and-modal-navigation',at:new Date().toISOString(),app:URL,status:'NOT_RUN',checks:{},details:{},errors:[],owner_data:'NEVER_ACCESSED',mutation:'NONE'};
const ck=(k,v,d)=>{out.checks[k]=!!v;if(d!==undefined)out.details[k]=d};let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const ctx=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844},reducedMotion:'reduce'});
 const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(155000);
 await page.goto(URL,{waitUntil:'domcontentloaded',timeout:100000});
 await page.waitForFunction(()=>{let x=document.getElementById('loading');return x&&getComputedStyle(x).display==='none'},null,{timeout:130000});
 await page.evaluate(()=>{const ob=document.getElementById('onboarding-overlay');if(ob&&getComputedStyle(ob).display!=='none')finishOnboarding()});
 ck('fresh_candidate_v14219',(await page.evaluate(()=>PUBLIC_VERSION))==='142.19');
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;await dbPut('settings',{key:'__R25_TEMP',val:'UNRELATED_DISPOSABLE_RECORD'})});
 // Exercises real app size overlay, focus trapping and escape dismissal; assertions do not assume native iOS.
 const dialog=await page.evaluate(async()=>{await showSizeSheet();return{visible:document.getElementById('size-overlay')?.classList.contains('show'),focused:document.activeElement?.tagName,focusInside:document.getElementById('size-overlay')?.contains(document.activeElement),role:document.getElementById('size-overlay')?.getAttribute('role')}});
 ck('size_dialog_opens_and_keyboard_focus_moves_into_modal',dialog.visible&&dialog.focusInside,dialog);
 await page.keyboard.press('Escape');await page.waitForTimeout(160);
 const dismissed=await page.evaluate(()=>({visible:document.getElementById('size-overlay')?.classList.contains('show'),activeScreen:document.querySelector('.screen.active')?.id}));
 ck('escape_closes_size_modal_without_escaping_screen',!dismissed.visible,dismissed);
 const screens=[];for(const name of ['goTomes','goHome','goEspace','goSearch','goHome']){
 const info=await page.evaluate(async method=>{await window[method]();return{method,screen:document.querySelector('.screen.active')?.id,rootOverflow:document.documentElement.scrollHeight-document.documentElement.clientHeight}},name);
 screens.push(info);}
 ck('major_screen_navigation_and_layout_stable',screens.every(x=>x.screen===('screen-'+({goTomes:'tomes',goHome:'home',goEspace:'espace',goSearch:'search'}[x.method]))&&x.rootOverflow<=5),screens);
 const first=await page.evaluate(async()=>await requestOfflineStatus());
 ck('offline_initial_state_has_authoritative_asset_universe',first.total===204,{state:first.state,total:first.total});
 await page.evaluate(async()=>await startOfflinePreparation());
 await page.waitForTimeout(130);
 await ctx.setOffline(true);await page.waitForTimeout(600);
 await page.evaluate(async()=>await cancelOfflinePreparation()).catch(()=>{});
 await page.waitForTimeout(1400);
 const interrupted=await page.evaluate(()=>({state:offlineUiState.state,completed:offlineUiState.completed,total:offlineUiState.total,job:offlineUiState.job_id,failed:offlineUiState.failed?.length||0}));
 ck('interrupted_offline_download_does_not_falsely_claim_ready',interrupted.state!=='READY'||interrupted.completed===204,interrupted);
 await ctx.setOffline(false);
 await page.evaluate(async()=>await startOfflinePreparation());
 await page.waitForFunction(()=>['READY','ERROR','PARTIAL'].includes(offlineUiState.state),null,{timeout:650000,polling:1500});
 const recovered=await page.evaluate(async()=>{let s=await requestOfflineStatus();return{state:s.state,total:s.total,completed:s.completed,failed:s.failed?.length||0,mark:(await dbGet('settings','__R25_TEMP'))?.val}});
 ck('interrupted_download_then_online_resume_all_204_integrity_verified',recovered.state==='READY'&&recovered.total===204&&recovered.completed===204&&recovered.failed===0,recovered);
 ck('resuming_offline_does_not_touch_disposable_notes_preferences',recovered.mark==='UNRELATED_DISPOSABLE_RECORD',recovered);
 await ctx.setOffline(true);
 await page.reload({waitUntil:'domcontentloaded',timeout:140000});
 await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 const cold=await page.evaluate(async()=>({version:PUBLIC_VERSION,status:(await requestOfflineStatus()).state,marker:(await dbGet('settings','__R25_TEMP'))?.val,offline:!navigator.onLine}));
 ck('cold_offline_after_interruption_recovery_reopens_complete',cold.version==='142.19'&&cold.status==='READY'&&cold.marker==='UNRELATED_DISPOSABLE_RECORD',cold);
 await ctx.setOffline(false);
 ck('no_unhandled_script_errors_during_interruption_recovery',errors.length===0,errors.slice(0,15));
 out.status=Object.values(out.checks).every(Boolean)?'PASS_SCOPED_R25':'FAIL_SCOPED_R25';
 await ctx.close();
}catch(e){out.errors.push(String(e?.stack||e));out.status='FAIL_OR_INCOMPLETE_R25'}
finally{fs.writeFileSync(ART,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2));if(browser)await browser.close().catch(()=>{})}
