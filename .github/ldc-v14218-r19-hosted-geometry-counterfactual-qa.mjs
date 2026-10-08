import fs from 'node:fs';
import {webkit, chromium} from 'playwright';

// QA-ONLY, R19: never writes the hosted application, user stores or existing R17 evidence.
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/ldc/';
const output='LDC_v142.18_R19_HOSTED_READER_GEOMETRY_COUNTERFACTUAL_QA.json';
const report={
 schema:'ldc-v14218-r19-hosted-independent-layout-counterfactual-v1',
 captured_at:new Date().toISOString(), hosted_url:APP,
 candidate_source:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 original_R17_blob:'520772bf17b9a7a80aa8eb041f2124b6cf1ba3e1',
 qa_only:true, application_mutation:false, physical_apple:false, contexts:{}, errors:[],
 browser_environment:{node:process.version,ci:process.env.GITHUB_ACTIONS||'unknown',runner:process.env.RUNNER_OS||'unknown'},
 status:'NOT_COMPLETED'
};
const scenarios={
 baseline:'',
 no_html_webkit_fill:'html{height:100% !important}',
 no_body_webkit_min:'body{min-height:0 !important}',
 body_fixed_dynamic:'body{height:100dvh !important;min-height:0 !important;max-height:100dvh !important}',
 body_fixed_100percent:'body{height:100% !important;min-height:0 !important;max-height:100% !important}',
 main_hard_containment:'#main-content{max-height:calc(100dvh - var(--nav-safe-h)) !important}',
 combined_root_containment:'html{height:100% !important}body{height:100dvh !important;min-height:0 !important;max-height:100dvh !important}'
};
const viewports=[
 {name:'iphone_portrait',w:390,h:844},
 {name:'iphone_landscape',w:844,h:390},
 {name:'ipad_landscape_like',w:1024,h:768}
];
async function measure(page){
 return page.evaluate(()=>{
  const selectors=['html','body','#main-content','.screen.active','#screen-reader','#reader-scroll','#reader-header','#reader-body','#nav'];
  const boxes={};
  for(const selector of selectors){
   const el=document.querySelector(selector);if(!el)continue;
   const cs=getComputedStyle(el),r=el.getBoundingClientRect();
   boxes[selector]={top:r.top,bottom:r.bottom,height:r.height,width:r.width,clientHeight:el.clientHeight,
    scrollHeight:el.scrollHeight,offsetHeight:el.offsetHeight,overflowY:cs.overflowY,display:cs.display,
    heightStyle:cs.height,minHeight:cs.minHeight,maxHeight:cs.maxHeight,flex:cs.flex,position:cs.position,
    paddingBottom:cs.paddingBottom,cssText:el.getAttribute('style')};
  }
  const sc=document.getElementById('reader-scroll');
  const before={documentY:window.scrollY,readerY:sc?.scrollTop||0};
  if(sc)sc.scrollTop=sc.scrollHeight;const atEnd={readerY:sc?.scrollTop||0,readerMax:sc?sc.scrollHeight-sc.clientHeight:0};
  if(sc)sc.scrollTop=before.readerY;
  const nav=document.getElementById('nav')?.getBoundingClientRect();
  const ss=boxes['#reader-scroll'];
  return {
   inner:{width:innerWidth,height:innerHeight,visualHeight:visualViewport?.height,
    htmlClientHeight:document.documentElement.clientHeight,htmlScrollHeight:document.documentElement.scrollHeight,
    windowScrollY:window.scrollY,windowScrollMax:document.documentElement.scrollHeight-document.documentElement.clientHeight},
   active:document.querySelector('.screen.active')?.id,currentEntry:typeof currentEntry==='object'?currentEntry?.id:null,
   readerChars:document.querySelector('#reader-body')?.innerText?.trim()?.length||0,
   bodyClass:document.body.className, readerScrollable:!!sc&&(sc.scrollHeight>sc.clientHeight+8),
   readerScrollEnd:atEnd, scrollReset:before,
   fitsViewport:!!ss&&ss.bottom<=innerHeight+3&&ss.top>=0&&ss.height>100,
   navStable:!!nav&&Math.abs(nav.bottom-innerHeight)<=3,
   navRect:nav?{top:nav.top,bottom:nav.bottom,height:nav.height}:null,
   boxes
  }
 });
}
async function snap(page,name) {
 const f='r19_'+name.replace(/[^a-z0-9_-]/gi,'_')+'.png';
 try {await page.screenshot({path:f,fullPage:false,timeout:20000});return f}
 catch(e){return 'SCREENSHOT_ERROR:'+String(e)}
}
async function runProbe(label, engine, opts, exe){
 let browser;
 const entry={cases:{},errors:[],browser_version:null};
 report.contexts[label]=entry;
 try{
  browser=await engine.launch({headless:true,...(exe?{executablePath:exe,args:['--no-sandbox']}:{})});
  entry.browser_version=browser.version();
  const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow',reducedMotion:'reduce',...opts});
  const page=await ctx.newPage();
  page.setDefaultTimeout(150000);
  page.on('pageerror',e=>entry.errors.push('PAGE:'+String(e)));
  await page.goto(APP,{waitUntil:'domcontentloaded',timeout:130000});
  await page.waitForFunction(()=>{const x=document.getElementById('loading');return x&&getComputedStyle(x).display==='none'},null,{timeout:150000});
  await page.evaluate(()=>{const x=document.getElementById('onboarding-overlay');if(x&&getComputedStyle(x).display!=='none')finishOnboarding()});
  await page.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
  await page.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>3,null,{timeout:160000});
  const cards=page.locator('#search-results .result-card');
  entry.first_result=await cards.first().innerText().then(s=>s.slice(0,240));
  const valid=cards.filter({hasNotText:/Explication éditoriale/i}).first();
  entry.selected_result=(await valid.innerText()).slice(0,240);
  await valid.click();
  await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:130000});
  for(const v of viewports){
   await page.setViewportSize({width:v.w,height:v.h});
   await page.waitForTimeout(300);
   const caseDetail={baseline:null,counterfactuals:{},reset:null};
   entry.cases[v.name]=caseDetail;
   caseDetail.baseline=await measure(page);
   caseDetail.screenshot=await snap(page,label+'_'+v.name+'_baseline');
   for (const [id,css] of Object.entries(scenarios)){
    if(id==='baseline')continue;
    const tag=await page.addStyleTag({content:css});
    await page.waitForTimeout(75);
    caseDetail.counterfactuals[id]=await measure(page);
    await tag.evaluate(e=>e.remove());
    await page.waitForTimeout(60);
   }
   caseDetail.reset=await measure(page);
   caseDetail.reset_invariant=Math.abs(caseDetail.baseline.boxes.body.height-caseDetail.reset.boxes.body.height)<3;
   // Short-content negative control tests whether content length contributes to overflow.
   caseDetail.short_content_control=await page.evaluate(()=>{
    const rb=document.getElementById('reader-body');if(!rb)return null;
    const prior=rb.style.display;rb.style.display='none';
    const a=document.querySelector('#reader-scroll').getBoundingClientRect();
    const out={readerScrollBottom:a.bottom,docScrollHeight:document.documentElement.scrollHeight,bodyHeight:document.body.getBoundingClientRect().height};
    rb.style.display=prior;return out;
   });
  }
  // Large Reader font to challenge flex shrink in landscape. Local page state only.
  await page.setViewportSize({width:844,height:390});
  entry.large_text=await page.evaluate(()=>{document.documentElement.style.setProperty('--reader-size','27px');return true});
  await page.waitForTimeout(250);
  entry.large_text_geometry=await measure(page);
  entry.large_text_screenshot=await snap(page,label+'_landscape_large_text');
  await ctx.close();
 }catch(e){entry.errors.push('PROBE:'+String(e?.stack||e))}
 finally{if(browser)await browser.close().catch(()=>{})}
}
try {
 await runProbe('webkit_mobile',webkit,{isMobile:true,hasTouch:true,deviceScaleFactor:2},null);
 await runProbe('webkit_desktop',webkit,{isMobile:false,hasTouch:false,deviceScaleFactor:1},null);
 await runProbe('chromium_mobile',chromium,{isMobile:true,hasTouch:true,deviceScaleFactor:2},'/usr/bin/google-chrome');
 await runProbe('chromium_desktop',chromium,{isMobile:false,hasTouch:false,deviceScaleFactor:1},'/usr/bin/google-chrome');
 const contexts=Object.values(report.contexts);
 const allRan=contexts.every(x=>Object.keys(x.cases).length===3&&!x.errors.length);
 const allFit=allRan&&contexts.every(x=>Object.values(x.cases).every(v=>v.baseline.fitsViewport&&v.baseline.navStable&&v.baseline.readerScrollable));
 report.status=allRan?(allFit?'PASS_LINUX_ENGINE_RESPONSIVE_GEOMETRY_SCOPED':'FAIL_LINUX_ENGINE_RESPONSIVE_GEOMETRY'):'INCOMPLETE_QA_OR_ENVIRONMENT';
} catch(e) {report.errors.push(String(e?.stack||e));report.status='INCOMPLETE_QA_OR_ENVIRONMENT'}
finally{
 fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,summary:Object.fromEntries(Object.entries(report.contexts).map(([id,x])=>[id,{version:x.browser_version,errors:x.errors,cases:Object.fromEntries(Object.entries(x.cases).map(([k,v])=>[k,{body:v.baseline?.boxes?.body?.height,scroll:v.baseline?.boxes?.['#reader-scroll']?.height,scrollBottom:v.baseline?.boxes?.['#reader-scroll']?.bottom,scrollable:v.baseline?.readerScrollable,fits:v.baseline?.fitsViewport,cf:Object.fromEntries(Object.entries(v.counterfactuals).map(([y,z])=>[y,{body:z.boxes?.body?.height,scroll:z.boxes?.['#reader-scroll']?.height,fit:z.fitsViewport,scrollable:z.readerScrollable}]))}]))}]))},null,2));
}
