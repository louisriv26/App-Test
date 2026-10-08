import fs from 'node:fs';
import {webkit,chromium} from 'playwright';
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/ldc/';
const out={schema:'ldc-v14218-r17-adversarial-actual-hosted-reader-viewport-comparison-v1',
 tested_at:new Date().toISOString(),app:APP,status:'NOT_RUN',checks:{},details:{},errors:[],
 source:'7c292d6221bb350fac3aeaa83750b8784706d45c',
 scope:'Actual live hosted app. Linux WebKit isMobile true and false; Chromium reference. No real iOS device or app source changes.',
 mutation_authority:'NONE',release_authority:'NONE',ios_gate:'OPEN'};
const ck=(n,v,d)=>{out.checks[n]=!!v;if(d!==undefined)out.details[n]=d};
async function probe(name,engine,opts){
 let browser,context;try{
  browser=await engine.launch({headless:true,...(name==='chromium'?{executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']}:{})});
  context=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844},...opts});
  const p=await context.newPage(),errors=[];p.setDefaultTimeout(150000);p.on('pageerror',e=>errors.push(String(e)));
  await p.goto(APP,{waitUntil:'domcontentloaded',timeout:130000});
  await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
  await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
  await p.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});
    setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
  await p.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>3,null,{timeout:160000});
  await p.locator('#search-results .result-card').filter({hasNotText:/Explication éditoriale/i}).first().click();
  await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:130000});
  async function geometry(){return await p.evaluate(()=>{
    const selectors=['html','body','#app','#screen-reader','#reader-scroll','#reader-header','#reader-body','#bottom-nav','#nav-bar','#tab-bar','.bottom-nav'];
    const layout={};for(const sel of selectors){const el=document.querySelector(sel);if(!el)continue;const r=el.getBoundingClientRect(),s=getComputedStyle(el);
      layout[sel]={top:Math.round(r.top),bottom:Math.round(r.bottom),height:Math.round(r.height),clientHeight:el.clientHeight,scrollHeight:el.scrollHeight,
       overflowY:s.overflowY,display:s.display,flex:s.flex,position:s.position,minHeight:s.minHeight,maxHeight:s.maxHeight};}
    const sc=document.getElementById('reader-scroll');const pre=sc.scrollTop;sc.scrollTop=150;const after=sc.scrollTop;sc.scrollTop=pre;
    return {viewport:{innerWidth,innerHeight,docClientH:document.documentElement.clientHeight,
      visualH:visualViewport?.height,windowOuterH:outerHeight},
      active:document.querySelector('.screen.active')?.id,entry:currentEntry?.id,readerChars:document.querySelector('#reader-body')?.innerText?.trim().length,
      layout,scrollMoved:after!==pre,bottomAtViewport:document.elementFromPoint(innerWidth-15,innerHeight-15)?.outerHTML?.slice(0,180)};});}
  const portrait=await geometry();await p.setViewportSize({width:844,height:390});await p.waitForTimeout(700);
  const landscape=await geometry();
  const badPortrait=portrait.layout['#reader-scroll']?.bottom>portrait.viewport.innerHeight+24;
  const badLandscape=landscape.layout['#reader-scroll']?.bottom>landscape.viewport.innerHeight+24;
  out.details[name]={portrait,landscape,pageErrors:errors,badPortrait,badLandscape};
  ck(name+'_reader_content_visible_both_orientations',portrait.readerChars>100&&landscape.readerChars>100&&portrait.entry===landscape.entry);
  ck(name+'_reader_scroll_container_within_viewport',!badPortrait&&!badLandscape,{portraitExcess:(portrait.layout['#reader-scroll']?.bottom||0)-portrait.viewport.innerHeight,
    landscapeExcess:(landscape.layout['#reader-scroll']?.bottom||0)-landscape.viewport.innerHeight});
  ck(name+'_reader_no_js_errors',errors.length===0,errors);
 }catch(e){out.errors.push(name+': '+String(e?.stack||e));ck(name+'_scenario_completed',false)}
 finally{if(browser)await browser.close().catch(()=>{})}
}
try{
 await probe('webkit_mobile',webkit,{isMobile:true,hasTouch:true,deviceScaleFactor:2});
 await probe('webkit_desktop_viewport',webkit,{isMobile:false,hasTouch:false,deviceScaleFactor:1});
 await probe('chromium_mobile',chromium,{isMobile:true,hasTouch:true,deviceScaleFactor:2});
 out.status=Object.values(out.checks).every(Boolean)&&!out.errors.length?'PASS_ALL_HOSTED_VIEWPORT_GEOMETRY_SCOPED':'FAIL_GEOMETRY_OR_QA';
}catch(e){out.status='FAIL_GEOMETRY_OR_QA';out.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync('LDC_v142.18_R17_MASSFINDERBETA_READER_VIEWPORT_GEOMETRY_QA.json',JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2))}
