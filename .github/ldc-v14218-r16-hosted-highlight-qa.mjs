import fs from 'node:fs';import {chromium} from 'playwright-core';
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/ldc/';
const out={schema:'ldc-v14218-r16-hosted-highlight-Reader-MonEspace-layout-QA-v1',status:'NOT_RUN',url:APP,
 tested_at:new Date().toISOString(),checks:{},details:{},errors:[],warnings:[],
 scope:'Fresh disposable real Chromium hosted site, canonical synthetic highlight via app persistence function; NOT native iOS text-selection equivalence',
 source:'7c292d6221bb350fac3aeaa83750b8784706d45c',mutation_authority:'NONE',deployment_authority:'NONE',physical_gate:'OPEN'};
const ck=(k,pass,detail)=>{out.checks[k]=!!pass;if(detail!==undefined)out.details[k]=detail};
let browser;try{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'}),p=await ctx.newPage(),errors=[];
 p.on('pageerror',e=>errors.push(String(e)));p.setDefaultTimeout(150000);
 await p.goto(APP,{waitUntil:'domcontentloaded',timeout:110000});
 await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
 ck('actual_hosted_candidate_boot_14218',(await p.evaluate(()=>PUBLIC_VERSION))==='142.18');
 await p.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
 await p.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>0,null,{timeout:160000});
 await p.locator('#search-results .result-card').first().click();
 await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:90000});
 const selection=await p.evaluate(async()=>{
  const frags=Array.from(document.querySelectorAll('#reader-body .para-fragment'));
  const possible=frags.map(e=>({el:e,para:e.dataset.paraId,rec:window.LDCAnchor?.recordFor(e)}))
   .filter(x=>x.para&&x.rec&&typeof x.rec.text==='string'&&x.rec.text.length>35&&Number.isFinite(x.rec.canonicalStart));
  const chosen=possible[0];if(!chosen)return {ok:false,fragCount:frags.length,candidates:possible.length};
  const start=chosen.rec.canonicalStart,end=Math.min(start+25,chosen.rec.canonicalEnd);
  const text=chosen.rec.text.slice(start,end);
  const exists=fragmentEl(chosen.para,start);
  const base={entryId:currentEntry.id,para:chosen.para,text,start,end,length:chosen.rec.text.length,color:ACTIVE_HIGHLIGHT_KEYS[0],
    canonicalStart:chosen.rec.canonicalStart,canonicalEnd:chosen.rec.canonicalEnd,matchingFragment:!!exists};
  if(text.length<10)return {...base,ok:false};
  const sc=document.getElementById('reader-scroll'),view={scrollTop:sc.scrollTop,semantic:captureSemanticReadingPosition()};
  await applyHighlight(base.color,[{para_id:chosen.para,start_char:start,end_char:end,text}],view);
  const rows=await dbGetAll('highlights');const marks=document.querySelectorAll('#reader-body mark.hl').length;
  return {...base,ok:rows.length===1,rows:rows.map(x=>({id:x.id,entry:x.entry_id,text:x.text,para:x.para_id,color:x.color})),paintedMarks:marks,
    scrollAfter:sc.scrollTop,scrollBefore:view.scrollTop};
 });
 ck('hosted_canonical_highlight_saved_in_actual_user_database',selection.ok&&selection.rows?.[0]?.text===selection.text&&selection.rows[0].entry===selection.entryId,selection);
 ck('hosted_new_highlight_painted_without_Reader_jump',selection.paintedMarks>0&&Math.abs(selection.scrollAfter-selection.scrollBefore)<16,
  {marks:selection.paintedMarks,before:selection.scrollBefore,after:selection.scrollAfter});
 await p.evaluate(async()=>{await goEspace();showEspaceTab('highlights')});
 await p.waitForFunction(()=>document.querySelectorAll('#ep-highlights .espace-item').length>0,null,{timeout:65000});
 const espace=await p.evaluate(()=>({count:document.querySelectorAll('#ep-highlights .espace-item').length,tab:activeEspaceTab,
  rowText:document.querySelector('#ep-highlights .espace-item')?.innerText?.slice(0,190)}));
 ck('hosted_new_highlight_findable_under_Mon_Espace',espace.count===1&&espace.tab==='highlights',espace);
 await p.locator('#ep-highlights .espace-item').first().click();
 await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:100000});
 await p.waitForTimeout(950);
 const opened=await p.evaluate(()=>{const body=document.getElementById('reader-body'),sc=document.getElementById('reader-scroll');
  const reader=document.getElementById('screen-reader'),rr=reader.getBoundingClientRect(),sr=sc.getBoundingClientRect();
  const style=getComputedStyle(sc);
  return {entry:currentEntry?.id,characters:body.innerText.trim().length,highlightMarks:body.querySelectorAll('mark.hl').length,
   viewportH:innerHeight,reader:{top:rr.top,bottom:rr.bottom,height:rr.height},
   scroll:{top:sr.top,bottom:sr.bottom,height:sr.height},cssOverflow:style.overflowY,
   scrollHeight:sc.scrollHeight,clientHeight:sc.clientHeight};
 });
 ck('hosted_Mon_Espace_highlight_link_opens_correct_nonblank_reader',
   opened.entry===selection.entryId&&opened.characters>100&&opened.highlightMarks>0,opened);
 ck('hosted_Mon_Espace_link_reader_scroll_not_collapsed_half_screen',
   opened.scroll.height>200&&opened.scroll.bottom>opened.viewportH*0.52&&opened.scroll.top>=0,opened);
 await p.reload({waitUntil:'domcontentloaded',timeout:120000});
 await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:130000});
 const pers=await p.evaluate(async()=>({saved:(await dbGetAll('highlights')).length,entry:(await dbGetAll('highlights'))[0]?.entry_id}));
 ck('hosted_highlight_persists_after_browser_reopen',pers.saved===1&&pers.entry===selection.entryId,pers);
 ck('hosted_highlight_no_unhandled_errors',errors.length===0,errors);
 out.status=Object.values(out.checks).every(Boolean)?'PASS_SCOPED_HOSTED_HIGHLIGHT_MON_ESPACE':'FAIL';
}catch(e){out.status='FAIL';out.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync('LDC_v142.18_R16_MASSFINDERBETA_HOSTED_HIGHLIGHT_QA.json',JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2));if(browser)await browser.close().catch(()=>{});}
