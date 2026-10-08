import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';

const SHA='v14218-ADVERSARIAL-DOM-R1';
const report={schema:'ldc-v14218-combined-dom-adversarial-r1',identity:SHA,
  status:'INCOMPLETE',checks:{},measurements:{},risks:[],errors:[],scope:'LOCAL_CHROMIUM_ONLY; no device/hosted/release claim'};
const port=8885,base='http://127.0.0.1:'+port;
let browser,server;
const check=(name,ok,extra=null)=>{report.checks[name]=!!ok;if(extra!==null)report.measurements[name]=extra};
const evalPage=async(page,script,arg)=>page.evaluate(script,arg);
try{
  server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
  await new Promise(r=>setTimeout(r,900));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
  const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
  const page=await context.newPage();page.setDefaultTimeout(180000);
  page.on('pageerror',e=>report.errors.push('PAGE:'+String(e)));
  page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP_'+r.status()+':'+r.url())});
  await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none'&&window.LDCPLSV16Runtime?.status,null,{timeout:120000});
  await evalPage(page,()=>{if(document.getElementById('onboarding-overlay')&&getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
  const boot=await evalPage(page,()=>({semantic:window.LDCPLSV16Runtime.status(),offlineBinding:OFFLINE_CONTENT_BINDING,readerOwner:typeof beginReaderProgrammaticScroll==='function',layoutHelper:typeof updateReaderLowHeightMode==='function'}));
  report.measurements.boot=boot;
  check('lazy_semantic_initialization',boot.semantic.ready===false);
  check('reader_ownership_present',boot.readerOwner&&boot.layoutHelper);
  const protocol=JSON.parse(fs.readFileSync('pls_v16/CALIBRATION_PROTOCOL_V2.json','utf8'));
  const query=protocol.positives.find(p=>p.id==='OWNER-REAL-02');
  await evalPage(page,async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},query.text);
  await page.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
  const initial=await evalPage(page,target=>{
    const r=searchLastPayload.payload.results;
    return {top:r[0]||null,count:r.length,rank:r.findIndex(x=>x.entry_id===target)+1,
      confidence:searchLastPayload.payload.confidence.state,returnedMode:supplementMode};
  },query.target_entry_id);
  report.measurements.semantic_positive={count:initial.count,rank:initial.rank,confidence:initial.confidence};
  check('positive_owner_rank_at_most_10',initial.rank>0&&initial.rank<=10&&initial.confidence==='possible');
  check('semantic_card_shown',await page.locator('#search-results .result-card').count()>0);
  const selected=initial.top;
  if(!selected)throw Error('missing positive result');
  // Each source mode must be measured rather than inferred; the pack searches enriched.
  const item=await evalPage(page,r=>semanticResultToSearchTargetR4(r),selected);
  for(const mode of ['enriched','aflp','additions']){
    let err=null;
    try{
      await evalPage(page,async input=>{
        await setSupplementMode(input.mode,{persist:false,origin:'user'});
        await openFromSearch(input.item);
      },{mode,item});
      await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:30000});
      await page.waitForTimeout(550);
      const opened=await evalPage(page,({expected,mode})=>{
        const sc=document.getElementById('reader-scroll');
        const para=expected.match_parts?.[0]?.para_id;
        const el=para?fragmentEl(para,0):null;
        const rect=el?.getBoundingClientRect(),view=sc?.getBoundingClientRect();
        return {mode,supplementMode,entry_id:currentEntry?.id||null,
          expected_entry:expected.entry_id,para_id:para,para_present:!!(el&&sc?.contains(el)),
          paragraph_visible:!!(rect&&view&&rect.bottom>view.top+12&&rect.top<view.bottom-12),
          scroller_height:sc?.clientHeight||0,body_length:document.getElementById('reader-body')?.innerText?.trim()?.length||0,
          root_scroll:document.scrollingElement?.scrollTop||0,intent:activeReaderSession?.intent||null}
      },{expected:item,mode});
      report.measurements['reader_'+mode]=opened;
      check('reader_'+mode+'_correct_entry',String(opened.entry_id)===String(item.entry_id));
      check('reader_'+mode+'_target',opened.para_present&&opened.paragraph_visible,opened);
      check('reader_'+mode+'_usable',opened.scroller_height>=65&&opened.body_length>0);
      if(mode==='enriched'){
        await page.setViewportSize({width:844,height:390});await page.waitForTimeout(500);
        const land=await evalPage(page,()=>({height:document.getElementById('reader-scroll')?.clientHeight||0,text:document.getElementById('reader-body')?.innerText?.trim()?.length||0}));
        await page.setViewportSize({width:390,height:844});await page.waitForTimeout(350);
        const port=await evalPage(page,()=>({height:document.getElementById('reader-scroll')?.clientHeight||0,text:document.getElementById('reader-body')?.innerText?.trim()?.length||0}));
        report.measurements.rotate_simulation={land,port};check('reader_responsive_nonempty',land.height>=65&&land.text>0&&port.height>=65&&port.text>0);
        const own=await evalPage(page,()=>{const a=beginReaderProgrammaticScroll(),b=beginReaderProgrammaticScroll();endReaderProgrammaticScroll(a);const still=ownsReaderProgrammaticScroll(b);endReaderProgrammaticScroll(b);return still});
        check('stale_scroll_epoch_rejection',own);
      }
      await page.locator('#reader-back-btn').click();
      await page.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active'),null,{timeout:30000});
      await page.waitForFunction(()=>!searchBusyGeneration&&searchLastPayload?.semantic===true,null,{timeout:180000});
    }catch(e){err=String(e);report.risks.push('MODE_'+mode+':'+err);
      check('reader_'+mode+'_target',false);
      await evalPage(page,async()=>{await goSearch();}).catch(()=>{});
    }
  }
  // Real model hard-negative false-positive control (not general scientific validation).
  for(const n of protocol.development_negatives.slice(0,3)){
    await evalPage(page,async q=>{await goSearch();setSearchIntentMode('meaning',{rerun:false,persist:false});setSearchQueryDraft(q,{mode:'meaning',syncOther:true});await runSearch()},n.text);
    await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:180000});
    const s=await evalPage(page,()=>({state:searchLastPayload?.semantic?searchLastPayload.payload?.confidence?.state:null,count:searchLastPayload?.payload?.results?.length||0}));
    report.measurements[n.id]=s;check('abstain_'+n.id,s.state==='abstain');
  }
  const memory=await evalPage(page,()=>({jsHeap:performance.memory?.usedJSHeapSize||null,total:performance.memory?.totalJSHeapSize||null,runtime:window.LDCPLSV16Runtime.status().phase||null}));
  report.measurements.memory_end=memory;
  report.status=Object.values(report.checks).every(Boolean)?'PASS':'FAIL';
}catch(e){report.errors.push(String(e?.stack||e));report.status='FAIL'}
finally{
  fs.writeFileSync('LDC_v142.18_ADVERSARIAL_DOM_QA.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  if(browser)await browser.close().catch(()=>{});
  if(server)server.kill('SIGTERM');
  if(report.status!=='PASS')process.exitCode=1;
}
