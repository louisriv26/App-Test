const fs=require('node:fs'),crypto=require('node:crypto');
const {chromium,webkit}=require('playwright');
const ROOT='https://louisriv26.github.io/App-Test/';
const manifest=JSON.parse(fs.readFileSync('PACKAGE_MANIFEST_SHA256.json','utf8'));
const reports=[];
function log(tag,fields={}){const v={tag,time:new Date().toISOString(),...fields};reports.push(v);console.log('R257_EXTENDED '+JSON.stringify(v))}
const wait=ms=>new Promise(res=>setTimeout(res,ms));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function get(path){
 let last;for(let n=0;n<3;n++){
  try{let r=await fetch(new URL(path,ROOT),{cache:'no-store'});
   if(!r.ok)throw new Error('HTTP '+r.status);
   return Buffer.from(await r.arrayBuffer());
  }catch(e){last=e;await wait(500*(n+1));}
 }throw new Error(path+' '+String(last));
}
async function inventory(){
 const list=manifest.files;const problems=[];
 let next=0,complete=0,bytes=0;
 async function worker(){
  while(next<list.length){
   let x=list[next++];try{
    let b=await get(x.path),hash=sha(b);bytes+=b.byteLength;
    if(b.length!==x.bytes||hash!==x.sha256)problems.push({path:x.path,expected:x.sha256,actual:hash,bytes:b.length});
   }catch(e){problems.push({path:x.path,error:String(e)});}
   complete++;
  }
 }
 await Promise.all(Array.from({length:12},worker));
 log('all_hosted_assets',{expected:list.length,checked:complete,bytes,mismatches:problems.slice(0,22),mismatchCount:problems.length});
 if(problems.length)throw Error('hosted asset parity FAIL '+problems.length);
}
function clip(s,max=550){return String(s||'').slice(0,max)}
async function runBrowser(browser,name,size){
 let context=await browser.newContext({serviceWorkers:'allow',viewport:size,locale:'fr-FR'}),page=await context.newPage();
 let errors=[];
 page.on('pageerror',e=>errors.push('PAGE '+String(e).slice(0,330)));
 page.on('console',e=>{if(e.type()==='error')errors.push('CONSOLE '+e.text().slice(0,240))});
 const tag=name+' '+size.width+'x'+size.height;
 try{
  await page.goto(ROOT+'?qa_r257='+Date.now(),{waitUntil:'domcontentloaded',timeout:70000});
  await page.waitForFunction(()=>typeof APP_VERSION!=='undefined' && bootStage==='POST_INIT' && getComputedStyle(document.querySelector('#loading')).display==='none',null,{timeout:70000});
  const boot=await page.evaluate(()=>({version:APP_VERSION,screen:currentScreenName(),home:document.querySelector('#screen-home')?.classList.contains('active'),verticalScroll:document.documentElement.scrollHeight,viewport:innerHeight,errors:document.querySelector('#boot-error-code')?.textContent||''}));
  log('boot',{tag,boot});
  if(boot.version!=='v2.19.142.46-R1B-UNIFIED'||boot.errors)throw Error('boot wrong version/error');
  await page.evaluate(async()=>{await goTomes();await openTome(7)});
  await page.waitForFunction(()=>document.getElementById('screen-entries')?.classList.contains('active')&&document.querySelectorAll('#entries-list .entry-item').length>5,null,{timeout:40000});
  const dates=await page.evaluate(()=>[...document.querySelectorAll('#entries-list .entry-item')].map(x=>x.dataset.entryDate).filter(Boolean).slice(0,8));
  log('tome7_entries',{tag,entries:await page.locator('#entries-list .entry-item').count(),dates});
  const candidates=page.locator('#entries-list .entry-item[data-entry-date="1906-01-30"]');
  let entry=candidates.count?await candidates.count():0;
  if(!entry){log('target_entry_not_found',{tag,date:'1906-01-30',sample:dates});}
  const target=entry?candidates.first():page.locator('#entries-list .entry-item').first();
  await target.click();
  await page.waitForFunction(()=>document.getElementById('screen-reader')?.classList.contains('active')&&document.querySelector('#reader-body .para-fragment'),null,{timeout:60000});
  const reader=await page.evaluate(()=>({textLen:document.getElementById('reader-body')?.innerText.length||0,fragmentCount:document.querySelectorAll('#reader-body .para-fragment').length,voiceRuns:document.querySelectorAll('#reader-body .speech-run').length,top:document.getElementById('reader-scroll')?.scrollTop,hasTargetText:document.getElementById('reader-body')?.innerText.includes('constance')}));
  log('reader',{tag,reader});
  if(reader.textLen<200||reader.fragmentCount<2)throw Error('Reader empty');
  // Local DOM Range selection: verifies selection geometry without modifying user storage.
  const geometry=await page.evaluate(async()=>{
   const sc=document.getElementById('reader-scroll');const start=sc.scrollTop;let nodes=[];
   const it=document.createTreeWalker(document.querySelector('#reader-body'),NodeFilter.SHOW_TEXT);
   while(it.nextNode()&&nodes.length<20){const n=it.currentNode;if(n.textContent.trim().length>18 && n.parentElement?.closest('.para-fragment'))nodes.push(n)}
   if(nodes.length<1)return {available:false};
   const n=nodes[0],range=document.createRange(),begin=Math.min(3,n.textContent.length-5);range.setStart(n,begin);range.setEnd(n,Math.min(begin+18,n.textContent.length));
   const sel=getSelection();sel.removeAllRanges();sel.addRange(range);document.dispatchEvent(new Event('selectionchange'));
   await new Promise(r=>setTimeout(r,800));
   const end=sc.scrollTop;
   const selected=sel.toString();
   sel.removeAllRanges();document.dispatchEvent(new Event('selectionchange'));
   return {available:true,selected:String(selected||'').slice(0,60),scrollBefore:start,scrollAfter:end,delta:end-start,fragments:document.querySelectorAll('#reader-body .para-fragment').length};
  });
  log('native_selection_geometry',{tag,geometry});
  if(!geometry.available||Math.abs(geometry.delta)>120)throw Error('unexpected reader selection jump');
  // Search word and meaning in real app; record separate lexical/semantic outcomes (fallback is not semantic PASS).
  await page.evaluate(async()=>{await goSearch();setSearchIntentMode('words',{rerun:false});const el=document.getElementById('search-input');el.value='constance';onSearchInput('words');await runSearch();});
  const lexical=await page.evaluate(()=>({meta:String(document.querySelector('#search-meta')?.innerText||'').slice(0,500),results:document.querySelector('#search-results')?.children.length||0,extract:String(document.querySelector('#search-results')?.innerText||'').slice(0,450)}));
  log('lexical_search',{tag,lexical});
  if(!lexical.results||/Aucun résultat/.test(lexical.extract))throw Error('lexical search has no results');
  await page.evaluate(async()=>{
    setSearchIntentMode('meaning',{rerun:false});
    const el=document.getElementById('search-input-meaning');
    el.value='Jésus explique comment la constance permet de persévérer dans le bien et de grandir spirituellement';
    onSearchInput('meaning');
    await runSearch();
  });
  const semantic=await page.evaluate(()=>({meta:String(document.querySelector('#search-meta')?.innerText||'').slice(0,550),resultCount:document.querySelector('#search-results')?.children.length||0,excerpt:String(document.querySelector('#search-results')?.innerText||'').slice(0,1200),progress:String(document.querySelector('#search-progress')?.innerText||'').slice(0,210)}));
  log('semantic_search',{tag,semantic});
  if(semantic.excerpt.includes('ni e Et si')||semantic.excerpt.includes('à l’i Il n’y')||semantic.excerpt.includes('de sorte  de telle sorte'))throw Error('malformed R198 semantic snippet surfaced');
  await page.evaluate(async()=>{await goHome()});
  log('navigation_back_home',{tag,home:await page.evaluate(()=>document.querySelector('#screen-home')?.classList.contains('active')),errors:errors.slice(0,8)});
  if(errors.length)log('browser_console_errors',{tag,count:errors.length,samples:errors.slice(0,7)});
  await page.screenshot({path:'r257-'+name.toLowerCase()+'-'+size.width+'x'+size.height+'.png',fullPage:false});
 }catch(e){log('scenario_error',{tag,error:String(e).slice(0,900),errors:errors.slice(0,8)});try{await page.screenshot({path:'r257-error-'+name.toLowerCase()+'-'+size.width+'x'+size.height+'.png'})}catch(_){};throw e}
 finally{await context.close()}
}
(async()=>{
 let ok=false;const failures=[];
 try{
  await inventory();
  for(let [name,engine] of [['Chromium',chromium],['WebKit',webkit]]){
   const browser=await engine.launch({headless:true});
   try{
    for(let size of [{width:1280,height:800},{width:390,height:844},{width:844,height:390}]){
      try{await runBrowser(browser,name,size)}catch(e){failures.push({browser:name,size,error:String(e)})}
    }
   }finally{await browser.close()}
  }
  ok=failures.length===0;
 }catch(e){failures.push({scope:'assets',error:String(e)})}
 log('FINAL',{ok,failures});
 fs.writeFileSync('r257-hosted-regressions.json',JSON.stringify({ok,failures,reports},null,2));
 if(!ok)process.exitCode=1;
})();
