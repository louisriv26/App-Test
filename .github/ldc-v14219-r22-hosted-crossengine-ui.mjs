import fs from 'node:fs';import {webkit,chromium} from 'playwright';
const APP='https://louisriv26.github.io/mauritius-mass-finder-beta/';
const REPORT='LDC_v142.19_R22_HOSTED_WEBKIT_CHROMIUM_UX_ACCESSIBILITY.json';
const out={schema:'ldc-v14219-r22-live-hosted-cross-engine-ux-v1',url:APP,tested_at:new Date().toISOString(),candidate_source:'0542656639432481c32bd70f354a6271b63dd93e',status:'NOT_RUN',scenarios:{},warnings:[],errors:[],ios_device:'NOT_TESTED',production_mutation:'NONE'};
const viewports=[{id:'portrait',width:390,height:844},{id:'landscape',width:844,height:390},{id:'ipad',width:1024,height:768},{id:'small',width:375,height:667}];
const safe=(s)=>s.replace(/[^a-z0-9_-]/gi,'_');
const metric=()=>{let sc=document.getElementById('reader-scroll'),r=sc?.getBoundingClientRect(),n=document.getElementById('nav')?.getBoundingClientRect();const first=Array.from(document.querySelectorAll('#reader-body .para-fragment')).find(x=>x.getBoundingClientRect().height>0);
 return{vh:innerHeight,vw:innerWidth,visualViewport:visualViewport?{h:visualViewport.height,w:visualViewport.width,offsetTop:visualViewport.offsetTop}:null,rootScrollMax:document.documentElement.scrollHeight-document.documentElement.clientHeight,rootScrollY:window.scrollY,
 bodyHeight:document.body.getBoundingClientRect().height,readerScrollTop:r?.top,readerScrollBottom:r?.bottom,readerScrollH:r?.height,scrollHeight:sc?.scrollHeight,clientHeight:sc?.clientHeight,
 readerTextLength:document.getElementById('reader-body')?.innerText.trim().length,entry:typeof currentEntry==='object'?currentEntry?.id:null,
 navTop:n?.top,navBottom:n?.bottom,navDisplay:document.getElementById('nav')?getComputedStyle(document.getElementById('nav')).display:null,lowHeight:document.body.classList.contains('reader-low-height'),firstParaTop:first?.getBoundingClientRect().top,
 textLevel:document.documentElement.getAttribute('data-text-level'),focused:document.activeElement?.tagName||null}};
async function run(label,engine,mobile,executablePath){
 const record={browser:null,version:null,events:[],checks:{},geometry:{},errors:[]};out.scenarios[label]=record;
 let browser;
 const ck=(n,v,d)=>{record.checks[n]=!!v;if(d!==undefined)record.events.push({name:n,detail:d})};
 try {
  browser=await engine.launch({headless:true,...(executablePath?{executablePath,args:['--no-sandbox']}:{})});record.browser=browser.version();
  const ctx=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:mobile?2:1,reducedMotion:'reduce'});
  const pg=await ctx.newPage();pg.setDefaultTimeout(150000);pg.on('pageerror',e=>record.errors.push(String(e)));
  await pg.goto(APP,{waitUntil:'domcontentloaded',timeout:120000});
  await pg.waitForFunction(()=>{let t=document.getElementById('loading');return t&&getComputedStyle(t).display==='none'},null,{timeout:150000});
  await pg.evaluate(()=>{let ob=document.getElementById('onboarding-overlay');if(ob&&getComputedStyle(ob).display!=='none')finishOnboarding()});
  record.version=await pg.evaluate(()=>({public:PUBLIC_VERSION,worker:SW_CACHE_VERSION}));
  ck('exact_hosted_application_version',record.version.public==='142.19',record.version);
  await pg.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
  await pg.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>=20,null,{timeout:170000});
  const cards=pg.locator('#search-results .result-card'),n=await cards.count();
  ck('lexical_results_visible_and_editorial_disambiguated',n===40&&/Explication éditoriale/i.test(await cards.first().innerText()),{cards:n});
  await cards.filter({hasNotText:/Explication éditoriale/i}).first().click();
  await pg.waitForFunction(()=>document.querySelector('#screen-reader')?.classList.contains('active'),null,{timeout:100000});
  const original=await pg.evaluate(metric);
  for(const v of viewports){
    await pg.setViewportSize({width:v.width,height:v.height});await pg.waitForTimeout(280);
    const x=await pg.evaluate(metric),moved=await pg.evaluate(()=>{const sc=document.getElementById('reader-scroll'),before=sc.scrollTop;sc.scrollTop=sc.scrollHeight;const end=sc.scrollTop;sc.scrollTop=before;return{end,max:sc.scrollHeight-sc.clientHeight}});
    record.geometry[v.id]={...x,scrollEnd:moved};
    ck('reader_'+v.id+'_contains_content_owns_scroll_and_root_still',x.readerTextLength>100&&x.entry===original.entry&&x.readerScrollTop>=0&&x.readerScrollBottom<=x.vh+3&&x.rootScrollMax<=4&&moved.max>50&&Math.abs(moved.end-moved.max)<2&&(!x.navBottom||Math.abs(x.navBottom-x.vh)<=3),{body:x.bodyHeight,scrollBottom:x.readerScrollBottom,scrollMax:moved.max,rootScroll:x.rootScrollMax,navDisplay:x.navDisplay,navBottom:x.navBottom});
    if(v.id==='portrait'||v.id==='landscape')try{await pg.screenshot({path:'R22_'+safe(label)+'_'+v.id+'.png',timeout:20000})}catch(e){record.errors.push('SCREENSHOT:'+e)}
  }
  await pg.setViewportSize({width:390,height:844});
  await pg.waitForTimeout(180);
  await pg.evaluate(()=>{const u=document.getElementById('size-overlay');if(u&&getComputedStyle(u).display==='none')u.classList.add('show')});
  await pg.evaluate(async()=>await setTextLevel('xlarge'));
  await pg.waitForTimeout(240);
  const large=await pg.evaluate(metric);
  ck('actual_application_text_size_xlarge_preserves_containment',large.textLevel==='xlarge'&&large.readerScrollBottom<=large.vh+3&&large.rootScrollMax<=4&&large.scrollHeight>large.clientHeight,large);
  await pg.setViewportSize({width:844,height:390});await pg.waitForTimeout(350);
  const largeLand=await pg.evaluate(metric);
  ck('xlarge_text_landscape_not_blank_and_scrollable',largeLand.readerTextLength>100&&largeLand.readerScrollBottom<=largeLand.vh+3&&largeLand.rootScrollMax<=4&&largeLand.scrollHeight>largeLand.clientHeight,largeLand);
  await pg.evaluate(async()=>await setTextLevel('normal'));
  await pg.setViewportSize({width:390,height:844});
  const terminal=await pg.evaluate(()=>{let sc=document.getElementById('reader-scroll');sc.scrollTop=sc.scrollHeight;return{pos:sc.scrollTop,max:sc.scrollHeight-sc.clientHeight}});
  ck('reader_last_paragraph_reachable_by_scrollTop',terminal.max>100&&Math.abs(terminal.pos-terminal.max)<2,terminal);
  await pg.evaluate(async()=>await goSearch());
  await pg.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active'),null,{timeout:100000});
  const search=await pg.evaluate(()=>({active:document.querySelector('.screen.active')?.id,cards:document.querySelectorAll('#search-results .result-card').length,rootScroll:document.documentElement.scrollHeight-document.documentElement.clientHeight}));
  ck('return_search_preserves_cards_and_scrolling',search.active==='screen-search'&&search.cards===40&&search.rootScroll<=4,search);
  await pg.evaluate(async()=>await goHome());
  const home=await pg.evaluate(()=>({active:document.querySelector('.screen.active')?.id,scrollHeight:document.documentElement.scrollHeight,viewport:innerHeight}));
  ck('home_screen_renders_after_reader',home.active==='screen-home',home);
  ck('zero_script_errors',record.errors.length===0,record.errors);
  await ctx.close();
 }catch(e){record.errors.push(String(e?.stack||e));record.checks.scenario_completed=false;}
 finally{record.pass=Object.values(record.checks).length>0&&Object.values(record.checks).every(Boolean)&&record.errors.length===0; if(browser)await browser.close().catch(()=>{});}
}
try {
 await run('webkit_mobile',webkit,true,null);
 await run('webkit_desktop',webkit,false,null);
 await run('chromium_mobile',chromium,true,'/usr/bin/google-chrome');
 await run('chromium_desktop',chromium,false,'/usr/bin/google-chrome');
 out.status=Object.values(out.scenarios).every(x=>x.pass)?'PASS_SCOPED_HOSTED_CROSS_ENGINE_UX':'FAIL_OR_UNQUALIFIED_HOSTED_CROSS_ENGINE';
}catch(e){out.status='FAIL_OR_UNQUALIFIED_HOSTED_CROSS_ENGINE';out.errors.push(String(e?.stack||e))}
finally{fs.writeFileSync(REPORT,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,cases:Object.fromEntries(Object.entries(out.scenarios).map(([k,v])=>[k,{version:v.browser,pass:v.pass,fails:Object.entries(v.checks).filter(([k,v])=>!v),errors:v.errors.slice(0,3)}]))},null,2))}
