import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';

const PORT=Number(process.env.LDC_WIP_E2E_PORT||8871);
const BASE='http://127.0.0.1:'+PORT;
const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8'));
const query=protocol.positives.find(x=>x.id==='OWNER-REAL-02');
if(!query)throw new Error('OWNER_QUERY_MISSING');
const report={schema:'ldc-pls-v16-real-app-navigation-qa-v1',status:'UNKNOWN',checks:{},details:{},errors:[],head:process.env.GITHUB_SHA||null,hosted_app_test_authorized:false,deployment_authorized:false};
let server=null,browser=null;
try{
 server=cp.spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:'.',stdio:['ignore','ignore','inherit']});
 await new Promise(r=>setTimeout(r,1000));
 const exe=process.env.CHROME_PATH||'/usr/bin/google-chrome';
 browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
 const page=await context.newPage();
 page.setDefaultTimeout(180000);
 page.on('pageerror',e=>report.errors.push('page:'+String(e)));
 page.on('console',m=>{if(m.type()==='error')report.errors.push('console:'+m.text())});
 page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP_'+r.status()+':'+r.url())});
 await page.goto(BASE+'/?wip_semantic_e2e=1',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>{
  const loading=document.getElementById('loading');
  const pill=document.getElementById('version-pill-home');
  return loading&&getComputedStyle(loading).display==='none'&&pill&&pill.textContent&&!/v—|v-$/.test(pill.textContent)&&typeof LDCPLSV16Runtime!=='undefined';
 },null,{timeout:120000});
 await page.evaluate(()=>{
  const overlay=document.getElementById('onboarding-overlay');
  if(overlay&&getComputedStyle(overlay).display!=='none')finishOnboarding();
 });
 report.checks.full_app_booted=true;
 const initial=await page.evaluate(()=>({version:PUBLIC_VERSION,semantic:LDCPLSV16Runtime.status(),user_db:typeof db!=='undefined'&&!!db}));
 report.details.initial=initial;
 report.checks.semantic_initially_lazy=initial.semantic.ready===false&&initial.semantic.available===false;
 await page.evaluate(async text=>{
   await goSearch();
   setSearchIntentMode('meaning',{rerun:false,persist:false});
   setSearchQueryDraft(text,{mode:'meaning',syncOther:true});
   await runSearch();
 },query.text);
 await page.waitForFunction(()=>document.querySelectorAll('#search-results .result-card').length>0&&searchLastPayload&&searchLastPayload.semantic===true,null,{timeout:180000});
 const found=await page.evaluate(()=> {
   const r=searchLastPayload.payload.results[0],s=(r.source_spans||[]).find(x=>x&&x.para_id)||null;
   const cards=[...document.querySelectorAll('#search-results .result-card')];
   return {entry_id:r.entry_id,volume:r.volume,passage_id:r.passage_id,para_id:s&&s.para_id,source_spans:(r.source_spans||[]).length,confidence:searchLastPayload.payload.confidence.state,cards:cards.length,first_card_key:cards[0]?.dataset.resultKey,visible:!!(cards[0]&&cards[0].getClientRects().length)};
 });
 report.details.selected=found;
 report.checks.semantic_app_search_displayed=found.cards>0&&found.visible&&found.confidence==='possible';
 report.checks.semantic_result_has_valid_reader_target=!!(found.entry_id&&Number(found.volume)>0&&found.para_id&&found.passage_id);
 if(!report.checks.semantic_result_has_valid_reader_target)throw new Error('SEMANTIC_RESULT_READER_TARGET_MISSING');
 await page.locator('#search-results .result-card').first().click({timeout:30000});
 await page.waitForFunction(target=>{
   const reader=document.getElementById('screen-reader');
   return reader&&reader.classList.contains('active')&&typeof currentEntry!=='undefined'&&currentEntry&&String(currentEntry.id)===String(target.entry_id)&&Number(currentVolume)===Number(target.volume);
 },found,{timeout:120000});
 await page.waitForTimeout(500);
 const opened=await page.evaluate(target=>{
  const sc=document.getElementById('reader-scroll');
  const frag=typeof fragmentEl==='function'?fragmentEl(target.para_id,0):null;
  const rect=frag&&frag.getBoundingClientRect(),cr=sc&&sc.getBoundingClientRect();
  return {entry_id:currentEntry&&currentEntry.id,volume:currentVolume,screen:document.getElementById('screen-reader')?.className,para_id:target.para_id,
   fragment_found:!!frag,fragment_visible:!!(rect&&cr&&rect.bottom>cr.top+15&&rect.top<cr.bottom-15),
   fragment_y:rect?Math.round(rect.top):null,scroll_top:sc&&sc.scrollTop,
   reader_has_text:!!(document.getElementById('reader-body')?.innerText||'').trim(),
   active_intent:typeof activeReaderSession!=='undefined'&&activeReaderSession?activeReaderSession.intent:null};
 },found);
 report.details.opened=opened;
 report.checks.semantic_result_opens_correct_entry=String(opened.entry_id)===String(found.entry_id)&&Number(opened.volume)===Number(found.volume);
 report.checks.semantic_result_paragraph_visible=opened.fragment_found&&opened.fragment_visible&&opened.reader_has_text;
 // Desktop-Chromium responsive-orientation challenge (not a substitute for iOS Safari).
 await page.setViewportSize({width:844,height:390});
 await page.waitForTimeout(450);
 const landscape=await page.evaluate(target=>({entry_id:currentEntry?.id||null,volume:currentVolume,body_text:document.getElementById('reader-body')?.innerText?.trim().length||0,reader_visible:!!document.getElementById('screen-reader')?.getClientRects().length}),found);
 await page.setViewportSize({width:390,height:844});
 await page.waitForTimeout(450);
 const portrait=await page.evaluate(target=>({entry_id:currentEntry?.id||null,volume:currentVolume,body_text:document.getElementById('reader-body')?.innerText?.trim().length||0,reader_visible:!!document.getElementById('screen-reader')?.getClientRects().length}),found);
 report.details.viewport_responsiveness={landscape,portrait};
 report.checks.reader_remains_visible_across_viewport_changes=[landscape,portrait].every(x=>x.entry_id===found.entry_id&&x.volume===Number(found.volume)&&x.body_text>0&&x.reader_visible);
 // Actual Return button, not programmatic navigation: the search results must survive.
 await page.locator('#reader-back-btn').click();
 await page.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active'),null,{timeout:30000});
 // The real Return handler intentionally reruns the search asynchronously; do not
 // confuse the intermediate cleared results pane with a failed restoration.
 await page.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>0,null,{timeout:180000});
 const returning=await page.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,query:searchQueryDraftCanonical(),semantic:!!searchLastPayload?.semantic}));
 report.details.return_to_search=returning;
 report.checks.return_preserves_semantic_results=returning.cards>0&&returning.query===query.text&&returning.semantic===true;

 report.checks.no_browser_errors=report.errors.length===0;
 report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
} catch(e){report.errors.push('HARNESS_OR_APP:'+String(e&&e.stack||e));report.status='FAIL';}
finally{
 fs.writeFileSync('wip-pls-v16-real-app-navigation-qa.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 if(server)server.kill('SIGTERM');
 if(report.status!=='PASS')process.exitCode=1;
}
