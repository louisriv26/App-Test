import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const report={schema:'ldc-v14218-reader-session-highlight-dom-v1',status:'UNKNOWN',checks:{},details:{},errors:[],source_sha:process.env.GITHUB_SHA||null,scope:'isolated local Chromium'};
let server,browser;
const set=(k,ok,v)=>{report.checks[k]=!!ok;report.details[k]=v;};
try{
 server=cp.spawn('python3',['-m','http.server','8923','--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,850));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
 const page=await ctx.newPage();page.setDefaultTimeout(180000);
 page.on('pageerror',e=>report.errors.push('JS:'+String(e)));
 await page.goto('http://127.0.0.1:8923/',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none'&&window.LDCPLSV16Runtime,null,{timeout:120000});
 await page.evaluate(()=>{if(getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
 const q=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8')).positives.find(p=>p.id==='OWNER-REAL-02').text;
 const before=await page.evaluate(async()=>({pos:await dbGetAll('reading_pos'),hl:await dbGetAll('highlights')}));
 set('fresh_private_profile',before.pos.length===0&&before.hl.length===0,{reading_pos:before.pos.length,highlights:before.hl.length});
 await page.evaluate(async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},q);
 await page.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
 const targets=await page.evaluate(()=>{
    const xs=searchLastPayload.payload.results.map(semanticResultToSearchTargetR4);
    return {a:xs[0],b:xs.find(x=>x.entry_id!==xs[0].entry_id)};
 });
 if(!targets.b)throw Error('no second distinct search result');
 await page.locator('#search-results .result-card').first().click();
 await page.waitForFunction(id=>document.getElementById('screen-reader')?.classList.contains('active')&&currentEntry?.id===id,targets.a.entry_id,{timeout:90000});
 const firstSession=await page.evaluate(()=>activeReaderSession?.session_id||null);
 const h=await page.evaluate(async()=>{
   const frag=document.querySelector('#reader-scroll .para-fragment');
   if(!frag)throw Error('missing canonical paragraph DOM');
   const rec=LDCAnchor.recordFor(frag);if(!rec)throw Error('missing canonical fragment record');
   const para_id=frag.dataset.paraId,text=rec.text.slice(0,Math.min(18,rec.text.length));
   if(!para_id||!text.trim())throw Error('invalid sample');
   const sc=document.getElementById('reader-scroll'),initial=sc.scrollTop;
   await applyHighlight('yellow',[{para_id,start_char:0,end_char:text.length,text}],{scrollTop:initial});
   const db=await dbGetAll('highlights');
   return {para_id,saved:db.filter(x=>x.para_id===para_id&&x.text===text).length,
     marks:document.querySelectorAll('#reader-scroll mark.hl').length,delta:Math.abs(sc.scrollTop-initial)};
 });
 set('real_highlight_persisted',h.saved===1,h);
 set('real_highlight_painted_and_scroll_stable',h.marks>0&&h.delta<=2,h);
 const rapid=await page.evaluate(async ({a,b})=>{
   const first=openFromSearch(a),second=openFromSearch(b);
   await Promise.allSettled([first,second]);
   await new Promise(r=>setTimeout(r,650));
   const sc=document.getElementById('reader-scroll'),target=fragmentEl(b.match_parts?.[0]?.para_id,0);
   const aRect=target?.getBoundingClientRect(),bRect=sc?.getBoundingClientRect();
   return {entry:currentEntry?.id,expected:b.entry_id,session:activeReaderSession?.session_id,
     bodyLength:document.getElementById('reader-body')?.innerText?.trim()?.length||0,
     targetVisible:!!(aRect&&bRect&&aRect.bottom>bRect.top+12&&aRect.top<bRect.bottom-12)};
 },targets);
 set('rapid_A_to_B_actual_DOM_latest_target_wins',rapid.entry===rapid.expected&&rapid.targetVisible&&rapid.bodyLength>0,rapid);
 const again=await page.evaluate(async b=>{
   const prior=activeReaderSession?.session_id;
   await openFromSearch(b);
   return {prior,newId:activeReaderSession?.session_id,entry:currentEntry?.id};
 },targets.b);
 set('same_visible_reader_rerender_preserves_session',again.prior===again.newId&&again.entry===targets.b.entry_id,again);
 await page.locator('#reader-back-btn').click();
 await page.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active')&&!searchBusyGeneration,null,{timeout:180000});
 const after=await page.evaluate(async()=>({pos:(await dbGetAll('reading_pos')).length,main:await dbGet('reading_pos','main'),highlights:(await dbGetAll('highlights')).length,
   cards:document.querySelectorAll('#search-results .result-card').length}));
 set('consultation_does_not_overwrite_authoritative_sequential_main',after.main==null,after);
 set('search_return_preserves_highlight_data',after.highlights===1&&after.cards>0,after);
 await page.locator('#search-results .result-card').first().click();
 await page.waitForFunction(id=>document.getElementById('screen-reader')?.classList.contains('active')&&currentEntry?.id===id,targets.a.entry_id,{timeout:90000});
 const persisted=await page.evaluate(async id=>({n:(await dbGetAll('highlights')).filter(h=>h.para_id===id).length,
    marks:document.querySelectorAll('#reader-scroll mark.hl').length,new_session:activeReaderSession?.session_id}),h.para_id);
 set('highlight_repainted_on_reader_reentry',persisted.n===1&&persisted.marks>0,persisted);
 set('new_reader_session_after_actual_search_return_and_reentry',!!firstSession&&persisted.new_session!==firstSession,{first:firstSession,second:persisted.new_session});
 set('no_unhandled_page_error',report.errors.length===0,report.errors);
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.status='FAIL';report.errors.push('HARNESS_OR_APP:'+String(e.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_SESSION_HIGHLIGHT_DOM_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
