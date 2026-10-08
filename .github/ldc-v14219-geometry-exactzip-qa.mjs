import fs from 'node:fs';
import {chromium,webkit} from 'playwright';
const APP='http://127.0.0.1:8997/';
const REPORT='LDC_v142.19_GEOMETRY_EXACT_ZIP_LOCAL_CROSS_ENGINE_QA.json';
const out={schema:'ldc-v14219-exact-repackaged-zip-actual-browser-v1',candidate:'UNRELEASED',tested_commit:process.env.GITHUB_SHA||'unknown',tested_at:new Date().toISOString(),url:APP,
 cases:{},errors:[],status:'NOT_RUN',physical_ios:'OPEN',test_deployment:'NONE',production_deployment:'NONE'};
const vp=[{key:'portrait',width:390,height:844},{key:'landscape',width:844,height:390},{key:'ipad',width:1024,height:768}];
function ensure(x,msg){if(!x)throw Error(msg)}
async function geometry(page){
 return await page.evaluate(()=>{
  const get=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return{top:r.top,bottom:r.bottom,height:r.height,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,overflowY:c.overflowY,position:c.position}};
  const read=get('#reader-scroll'),nav=get('#nav');
  const scroll=document.getElementById('reader-scroll');
  const before=scroll.scrollTop;scroll.scrollTop=scroll.scrollHeight;
  const end=scroll.scrollTop,maximum=scroll.scrollHeight-scroll.clientHeight;
  scroll.scrollTop=before;
  return {innerHeight,htmlHeight:document.documentElement.clientHeight,htmlScrollHeight:document.documentElement.scrollHeight,
   documentScrollTop:window.scrollY,body:get('body'),main:get('#main-content'),reader:read,readerBody:get('#reader-body'),
   nav,entry:typeof currentEntry==='object'?currentEntry?.id:null,readerChars:document.getElementById('reader-body')?.innerText?.trim().length||0,
   paneFits:!!read&&read.bottom<=innerHeight+3&&read.top>=0,
   navFits:!!nav&&Math.abs(nav.bottom-innerHeight)<=3,
   rootScrollMax:document.documentElement.scrollHeight-document.documentElement.clientHeight,
   readerScrollMax:maximum,readerMoved:end>0&&maximum>0&&Math.abs(end-maximum)<=2,
   atEnd:end};
 });
}
async function run(label, engine, options,executablePath){
 const item={browserVersion:null,errors:[],firstCard:null,selectedCard:null,viewports:{},large:null,back:null,nonReader:{},counterfactuals:{}};
 out.cases[label]=item;let browser;
 try{
  browser=await engine.launch({headless:true,...(executablePath?{executablePath,args:['--no-sandbox']}:{})});
  item.browserVersion=browser.version();
  const cx=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844},reducedMotion:'reduce',...options});
  const p=await cx.newPage();
  p.setDefaultTimeout(145000);p.on('pageerror',e=>item.errors.push(String(e)));
  await p.goto(APP,{waitUntil:'domcontentloaded',timeout:135000});
  await p.waitForFunction(()=>{const el=document.getElementById('loading');return el&&getComputedStyle(el).display==='none'},null,{timeout:150000});
  await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
  item.version=await p.evaluate(()=>({app:typeof APP_VERSION==='string'?APP_VERSION:null,worker:typeof SW_CACHE_VERSION==='string'?SW_CACHE_VERSION:null}));
  ensure(item.version.app==='v2.19.142.19-R1B-READER-GEOMETRY-CANDIDATE','APP_VERSION_MISMATCH');
  await p.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false,persist:false});setSearchQueryDraft('volonté',{mode:'words',syncOther:true});await runSearch()});
  await p.waitForFunction(()=>!searchBusyGeneration&&document.querySelectorAll('#search-results .result-card').length>3,null,{timeout:160000});
  const cards=p.locator('#search-results .result-card');item.firstCard=(await cards.first().innerText()).slice(0,220);
  const passage=cards.filter({hasNotText:/Explication éditoriale/i}).first();
  item.selectedCard=(await passage.innerText()).slice(0,220);
  await passage.click();
  await p.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active'),null,{timeout:150000});
  let entry0=null;
  for(const v of vp){
   await p.setViewportSize({width:v.width,height:v.height});
   await p.waitForTimeout(240);
   const m=await geometry(p);
   entry0??=m.entry;
   item.viewports[v.key]=m;
   item.viewports[v.key].pass=m.readerChars>100&&m.entry===entry0&&m.paneFits&&m.navFits&&m.readerMoved&&m.rootScrollMax<=3;
   try{await p.screenshot({path:'v14219_'+label+'_'+v.key+'.png',timeout:20000})}catch(e){item.errors.push('SCREENSHOT:'+String(e))}
  }
  await p.setViewportSize({width:390,height:844});
  await p.waitForTimeout(250);
  const rotated=await geometry(p);item.rotatedBack={...rotated,pass:rotated.entry===entry0&&rotated.paneFits&&rotated.readerMoved&&rotated.navFits};
  // Reinsert exactly the old offending rule as a reversible diagnostic, never into files.
  const broken=await p.addStyleTag({content:'html{height:-webkit-fill-available !important}'});
  await p.waitForTimeout(150);
  item.counterfactuals.reintroduced_old_root_fill=await geometry(p);
  await broken.evaluate(el=>el.remove());
  await p.waitForTimeout(150);
  item.counterfactuals.removal_restores=await geometry(p);
  // Large text at landscape is a separate bounded layout challenge.
  await p.setViewportSize({width:844,height:390});
  await p.evaluate(()=>document.documentElement.style.setProperty('--reader-size','27px'));
  await p.waitForTimeout(160);
  item.large=await geometry(p);item.large.pass=item.large.paneFits&&item.large.readerMoved&&item.large.navFits&&item.large.rootScrollMax<=3;
  await p.evaluate(()=>document.documentElement.style.removeProperty('--reader-size'));
  await p.evaluate(async()=>await goSearch());
  await p.waitForFunction(()=>document.getElementById('screen-search')?.classList.contains('active'),null,{timeout:70000});
  item.back=await p.evaluate(()=>({active:document.querySelector('.screen.active')?.id,cards:document.querySelectorAll('#search-results .result-card').length,bodyHeight:document.body.getBoundingClientRect().height,rootScrollMax:document.documentElement.scrollHeight-document.documentElement.clientHeight}));
  await p.evaluate(async()=>await goHome());
  await p.waitForTimeout(140);
  item.nonReader.home=await p.evaluate(()=>({active:document.querySelector('.screen.active')?.id,bodyHeight:document.body.getBoundingClientRect().height,rootScrollMax:document.documentElement.scrollHeight-document.documentElement.clientHeight,viewport:innerHeight}));
  // Chromium and WebKit are independent QA, not physical Safari.
  item.pass=Object.values(item.viewports).every(x=>x.pass)&&item.rotatedBack.pass&&item.large.pass&&item.counterfactuals.removal_restores.paneFits&&item.counterfactuals.removal_restores.readerMoved&&item.back.cards>3&&item.back.active==='screen-search'&&item.nonReader.home.active==='screen-home'&&item.errors.length===0;
  await cx.close();
 }catch(e){item.errors.push('PROBE_ERROR:'+String(e?.stack||e));item.pass=false}
 finally{if(browser)await browser.close().catch(()=>{})}
}
try{
 await run('webkit_mobile',webkit,{isMobile:true,hasTouch:true,deviceScaleFactor:2},null);
 await run('webkit_desktop',webkit,{isMobile:false,hasTouch:false,deviceScaleFactor:1},null);
 await run('chromium_mobile',chromium,{isMobile:true,hasTouch:true,deviceScaleFactor:2},'/usr/bin/google-chrome');
 await run('chromium_desktop',chromium,{isMobile:false,hasTouch:false,deviceScaleFactor:1},'/usr/bin/google-chrome');
 out.status=Object.values(out.cases).every(c=>c.pass)&&!out.errors.length?'PASS_EXACT_ZIP_LINUX_ENGINES_SCOPED':'FAIL_OR_INCOMPLETE_EXACT_ZIP_LINUX_ENGINES';
}catch(e){out.errors.push(String(e));out.status='FAIL_OR_INCOMPLETE_EXACT_ZIP_LINUX_ENGINES'}
finally{fs.writeFileSync(REPORT,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,cases:Object.fromEntries(Object.entries(out.cases).map(([k,v])=>[k,{pass:v.pass,errors:v.errors,viewport:Object.fromEntries(Object.entries(v.viewports).map(([n,m])=>[n,{pass:m.pass,rootMax:m.rootScrollMax,scrollMax:m.readerScrollMax,body:m.body?.height,reader:m.reader?.height,within:m.paneFits}]))}]))},null,2))}
