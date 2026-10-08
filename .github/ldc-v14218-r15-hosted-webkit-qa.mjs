import fs from 'node:fs';
import {webkit} from 'playwright';
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/ldc/';
const r={schema:'ldc-v14218-r15-actual-hosted-linux-webkit-independent-qa-v2-navigation-probe',
 tested_at:new Date().toISOString(),url:APP,status:'NOT_RUN',checks:{},details:{},errors:[],
 scope:'Real hosted MassFinderBeta, actual Linux Playwright WebKit; NOT iOS Safari/physical iPhone or iPad; disposable browsing session.',
 deployment_authority:'NONE',iOS_gate:'OPEN'};
const ck=(n,ok,d)=>{r.checks[n]=!!ok;if(d!==undefined)r.details[n]=d};
let browser;
try{
 browser=await webkit.launch({headless:true});
 const ctx=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const page=await ctx.newPage(),err=[],failed=[];
 page.setDefaultTimeout(180000);page.on('pageerror',e=>err.push(String(e)));
 page.on('requestfailed',req=>failed.push({url:req.url().slice(-110),reason:req.failure()}));
 await page.goto(APP,{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
 await page.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
 const boot=await page.evaluate(()=>({version:PUBLIC_VERSION,db:DB_NAME,screen:document.querySelector('.screen.active')?.id,viewport:{w:window.innerWidth,h:window.innerHeight}}));
 ck('real_hosted_Linux_WebKit_mobile_app_boot',boot.version==='142.18'&&boot.db==='ldc_user_v1'&&boot.screen==='screen-home',boot);
 await page.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
 await page.waitForFunction(()=>!searchBusyGeneration,null,{timeout:180000});
 const lex=await page.evaluate(()=>({count:document.querySelectorAll('#search-results .result-card').length,busy:!!searchBusyGeneration}));
 ck('hosted_Linux_WebKit_real_lexical_search',lex.count>0&&!lex.busy,lex);
 const firstCard=await page.locator('#search-results .result-card').first().evaluate(el=>({text:el.innerText.slice(0,180),html:el.outerHTML.slice(0,850),tag:el.tagName}));
 r.details.first_clicked_card=firstCard;
 await page.locator('#search-results .result-card').first().click();
 let opened=false;
 try{await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:55000});opened=true}
 catch(e){r.warnings=[{type:'WEBKIT_READER_NAVIGATION_TIMEOUT',message:String(e).slice(0,250)}]}
 const diagnostic=await page.evaluate(()=>({
   screens:[...document.querySelectorAll('.screen.active')].map(e=>e.id), currentEntryId:typeof currentEntry!=='undefined'?currentEntry?.id:null,
   selectedSearchResult:searchLastPayload?.payload?.results?.[0]?.entry_id||null,
   loading:document.getElementById('loading')?getComputedStyle(document.getElementById('loading')).display:null,
   readerText:document.getElementById('reader-body')?.innerText?.trim().length||0,
   readerActive:document.getElementById('screen-reader')?.classList.contains('active'),
   results:document.querySelectorAll('#search-results .result-card').length,
   bodyText:document.body.innerText.slice(-550),
   location:location.href
 }));
 r.details.navigation_after_55s={opened,diagnostic,jsErrors:err.slice(-20),failedRequests:failed.slice(-20)};
 ck('hosted_Linux_WebKit_search_result_enters_Reader',opened,diagnostic);
 if(!opened)throw Error('WEBKIT_READER_DID_NOT_OPEN_AFTER_CLICK__SEE_DIAGNOSTICS');
 const before=await page.evaluate(()=>({entry:currentEntry?.id,characters:document.querySelector('#reader-body')?.innerText?.trim().length||0,
  readerScroll:document.getElementById('reader-scroll')?.getBoundingClientRect().toJSON(),viewport:{w:window.innerWidth,h:window.innerHeight}}));
 ck('hosted_Linux_WebKit_Reader_content_visible_portrait',before.characters>100&&before.readerScroll.height>100,before);
 await page.setViewportSize({width:844,height:390});await page.waitForTimeout(1300);
 const landscape=await page.evaluate(()=>({entry:currentEntry?.id,characters:document.querySelector('#reader-body')?.innerText?.trim().length||0,
  readerScroll:document.getElementById('reader-scroll')?.getBoundingClientRect().toJSON(),viewport:{w:window.innerWidth,h:window.innerHeight}}));
 ck('hosted_Linux_WebKit_Reader_not_blank_landscape',landscape.characters>100&&landscape.entry===before.entry&&landscape.readerScroll.height>42,landscape);
 await page.setViewportSize({width:1024,height:768});await page.waitForTimeout(700);
 const tablet=await page.evaluate(()=>({text:document.querySelector('#reader-body')?.innerText?.trim().length||0,scrollHeight:document.querySelector('#reader-scroll')?.clientHeight||0}));
 ck('hosted_Linux_WebKit_tablet_viewport_Reader_survives',tablet.text>100&&tablet.scrollHeight>150,tablet);
 await page.setViewportSize({width:390,height:844});await page.locator('#reader-back-btn').click();
 await page.waitForFunction(()=>document.querySelector('#screen-search')?.classList.contains('active'),null,{timeout:90000});
 try{await page.waitForFunction(()=>document.querySelectorAll('#search-results .result-card').length>0,null,{timeout:18000})}catch(e){}
 const back=await page.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,q:searchQueryDraftCanonical(),screen:document.querySelector('.screen.active')?.id}));
 ck('hosted_Linux_WebKit_Reader_back_restores_search',back.cards>0&&back.q==='volonté'&&back.screen==='screen-search',back);
 ck('hosted_Linux_WebKit_no_runtime_js_errors',err.length===0,{errors:err.slice(0,20),failed:failed.slice(0,20)});
 r.status=Object.values(r.checks).every(Boolean)?'PASS_SCOPED_HOSTED_LINUX_WEBKIT':'FAIL';
}catch(e){r.status='FAIL';r.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync('LDC_v142.18_R15_MASSFINDERBETA_HOSTED_WEBKIT_QA.json',JSON.stringify(r,null,2)+'\n');
 console.log(JSON.stringify({status:r.status,checks:r.checks,errors:r.errors},null,2));if(browser)await browser.close().catch(()=>{});}
