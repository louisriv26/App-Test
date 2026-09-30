const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = process.cwd();
const specs = [
  {key:'24H', dir:'24h-v119-b1-prephysical', url:'https://louisriv26.github.io/App-Test/24h-v119-b1-prephysical/'},
  {key:'LDC', dir:'ldc-v132-b1-prephysical', url:'https://louisriv26.github.io/App-Test/ldc-v132-b1-prephysical/'},
  {key:'Lettres', dir:'lettres-v2.10-b1-prephysical', url:'https://louisriv26.github.io/App-Test/lettres-v2.10-b1-prephysical/'}
];
const report={generated_at:new Date().toISOString(), served_byte_parity:{}, apps:{}, overall:'UNKNOWN'};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function walk(dir){
  const out=[];
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    const p=path.join(dir,e.name);
    if(e.isDirectory()) out.push(...walk(p)); else out.push(p);
  }
  return out;
}
function ujoin(base, rel){ return new URL(rel.split('/').map(encodeURIComponent).join('/'),base).href; }
async function servedParity(spec){
  const root=path.join(ROOT,spec.dir);
  const files=walk(root).filter(p=>path.basename(p)!=='.nojekyll');
  const rows=[]; let idx=0;
  async function worker(){
    while(true){
      const i=idx++; if(i>=files.length) return;
      const p=files[i], rel=path.relative(root,p).split(path.sep).join('/');
      let ok=false,status=null,got=null,err=null;
      for(let attempt=0;attempt<3&&!ok;attempt++){
        try{
          const r=await fetch(ujoin(spec.url,rel),{cache:'no-store'});
          status=r.status;
          if(r.ok){ const b=Buffer.from(await r.arrayBuffer()); got=sha(b); ok=(got===sha(fs.readFileSync(p))); }
          if(!ok) await new Promise(r=>setTimeout(r,1000*(attempt+1)));
        }catch(e){err=String(e); await new Promise(r=>setTimeout(r,1000*(attempt+1)));}
      }
      rows.push({path:rel,status,ok,expected:sha(fs.readFileSync(p)),got,error:err});
    }
  }
  await Promise.all(Array.from({length:12},worker));
  const bad=rows.filter(x=>!x.ok);
  return {file_count:rows.length,pass:bad.length===0,bad};
}
async function swInfo(page){
  return await page.evaluate(async()=>{
    if(!('serviceWorker' in navigator)) return {supported:false};
    try{
      const reg=await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('SW ready timeout')),20000))]);
      return {supported:true,scope:reg.scope,active:reg.active&&reg.active.scriptURL,controller:!!navigator.serviceWorker.controller};
    }catch(e){return {supported:true,error:String(e),controller:!!navigator.serviceWorker.controller};}
  });
}
async function idbProbe(page){
  return await page.evaluate(async()=>{
    if(!('indexedDB' in self)) return {supported:false};
    const name='cl-prephysical-probe-'+Date.now();
    try{
      await new Promise((res,rej)=>{const q=indexedDB.open(name,1);q.onupgradeneeded=()=>q.result.createObjectStore('x');q.onsuccess=()=>{q.result.close();res();};q.onerror=()=>rej(q.error);});
      indexedDB.deleteDatabase(name); return {supported:true,pass:true};
    }catch(e){return {supported:true,pass:false,error:String(e)};}
  });
}
async function commonStart(browser,spec){
  const context=await browser.newContext({serviceWorkers:'allow',viewport:{width:1280,height:900}});
  const page=await context.newPage(); const errors=[];
  page.on('pageerror',e=>errors.push('pageerror:'+String(e)));
  page.on('console',m=>{if(m.type()==='error') errors.push('console:'+m.text());});
  const resp=await page.goto(spec.url,{waitUntil:'domcontentloaded',timeout:45000});
  await page.waitForTimeout(1200);
  let sw=await swInfo(page);
  if(sw.supported && !sw.error && !sw.controller){
    await page.reload({waitUntil:'domcontentloaded',timeout:45000}); await page.waitForTimeout(800); sw=await swInfo(page);
  }
  return {context,page,errors,http_status:resp&&resp.status(),sw,idb:await idbProbe(page)};
}
async function offlineCold(context,url,checkFn){
  await context.setOffline(true);
  const p=await context.newPage(); const errors=[];
  p.on('pageerror',e=>errors.push(String(e)));
  let navOk=true,navError=null;
  try{await p.goto(url,{waitUntil:'domcontentloaded',timeout:20000});}catch(e){navOk=false;navError=String(e);}
  await p.waitForTimeout(800);
  let state=null; try{state=await checkFn(p);}catch(e){state={error:String(e)};}
  await p.close(); await context.setOffline(false);
  return {nav_ok:navOk,nav_error:navError,state,errors};
}
async function test24(browser,spec){
  const x=await commonStart(browser,spec), p=x.page;
  const out={http_status:x.http_status,sw:x.sw,idb:x.idb,errors:x.errors};
  out.identity=await p.evaluate(()=>({version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,seq:typeof APP_RELEASE_SEQUENCE!=='undefined'?APP_RELEASE_SEQUENCE:null,id:typeof APP_RELEASE_ID!=='undefined'?APP_RELEASE_ID:null,evidence:typeof APP_EVIDENCE_STAGE!=='undefined'?APP_EVIDENCE_STAGE:null}));
  out.desktop_geometry=await p.evaluate(()=>{const n=document.querySelector('.bottom-nav'),c=document.getElementById('content');if(!n||!c)return null;const a=n.getBoundingClientRect(),b=c.getBoundingClientRect();return{position:getComputedStyle(n).position,vertical_overlap:Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top))};});
  try{
    await p.evaluate(()=>openHour(1,false)); await p.waitForTimeout(120);
    out.race_setup=await p.evaluate(()=>{const el=document.querySelector('[data-para-id] .para-text, [data-para-id]');if(!el)return{ok:false};const node=[...el.childNodes].find(n=>n.nodeType===3&&n.textContent.trim().length>8)||el.firstChild;if(!node||node.nodeType!==3)return{ok:false};const r=document.createRange();r.setStart(node,0);r.setEnd(node,Math.min(8,node.textContent.length));const sel=window.getSelection();sel.removeAllRanges();sel.addRange(r);handleSelectionEnd();showHome();return{ok:true,view:state.view};});
    await p.waitForTimeout(220);
    out.race_after_home=await p.evaluate(()=>({view:state.view,pending:!!state._pending,finalizeTimer:!!_selectionFinalizeTimer,captureTimer:!!_selectionCaptureTimer,toolbarVisible:[...document.querySelectorAll('.selection-actions,.action-bar,.selection-action-bar')].some(e=>getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0)}));
    await p.evaluate(()=>showSearchView(false,{query:'couronne',filter:'all',speaker:'all',scrollTop:0,focusId:'homeSearchInput'})); await p.waitForTimeout(180);
    const n=await p.locator('.search-result-item').count(); out.search={count:n};
    if(n){await p.locator('.search-result-item').first().click();await p.waitForTimeout(750);Object.assign(out.search,await p.evaluate(()=>({view:state.view,flash:document.querySelectorAll('.search-destination-flash').length,selection:String(window.getSelection()||'')})));}
  }catch(e){out.flow_error=String(e);}
  await p.emulateMedia({forcedColors:'active'});
  out.forced_colors=await p.evaluate(()=>Object.fromEntries(['.bn-item','.mark-btn','.mark-read-btn'].map(sel=>{const e=document.querySelector(sel);if(!e)return[sel,null];const c=getComputedStyle(e);return[sel,{width:c.borderWidth,style:c.borderStyle}];})));
  out.offline=await offlineCold(x.context,spec.url,async q=>q.evaluate(()=>({version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,view:typeof state!=='undefined'?state.view:null,body:document.body.innerText.length})));
  await p.close();await x.context.close();
  out.pass=out.http_status===200&&out.idb.pass&&out.sw.active&&out.identity.version==='v119'&&out.race_after_home&&out.race_after_home.view==='home'&&!out.race_after_home.pending&&!out.race_after_home.toolbarVisible&&out.search&&out.search.count>0&&out.search.flash>0&&out.offline.nav_ok&&out.offline.state&&out.offline.state.version==='v119';
  return out;
}
async function testLDC(browser,spec){
  const x=await commonStart(browser,spec), p=x.page;
  const out={http_status:x.http_status,sw:x.sw,idb:x.idb,errors:x.errors};
  await p.waitForTimeout(1000);
  out.identity=await p.evaluate(()=>({app:typeof APP_VERSION!=='undefined'?APP_VERSION:null,pub:typeof PUBLIC_VERSION!=='undefined'?PUBLIC_VERSION:null,swExpected:typeof SW_CACHE_VERSION!=='undefined'?SW_CACHE_VERSION:null}));
  try{
    out.d07=await p.evaluate(async()=>{try{localStorage.setItem(SEARCH_INTENT_MODE_KEY,'meaning')}catch(e){};setSearchIntentMode('meaning',{rerun:false,persist:false});await goSearch();return{mode:searchIntentMode,words:document.getElementById('search-intent-words')?.getAttribute('aria-pressed'),meaning:document.getElementById('search-intent-meaning')?.getAttribute('aria-pressed'),stored:localStorage.getItem(SEARCH_INTENT_MODE_KEY)};});
  }catch(e){out.d07={error:String(e)};}
  out.storage=await p.evaluate(async()=>{try{const api=navigator.storage||{};const e=api.estimate?await api.estimate():null;const persisted=api.persisted?await api.persisted():null;return{estimate:e,persisted};}catch(e){return{error:String(e)}}});
  out.public_copy=await p.evaluate(()=>({lab:(document.body.innerText.match(/LAB interne/gi)||[]).length,laboratoire:(document.body.innerText.match(/laboratoire/gi)||[]).length}));
  out.offline=await offlineCold(x.context,spec.url,async q=>q.evaluate(()=>({version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,swExpected:typeof SW_CACHE_VERSION!=='undefined'?SW_CACHE_VERSION:null,body:document.body.innerText.length})));
  await p.close();await x.context.close();
  out.pass=out.http_status===200&&out.idb.pass&&out.sw.active&&out.identity.app==='132'&&out.identity.pub==='132'&&out.identity.swExpected==='ldc-v132-b1-final-prephysical'&&out.d07&&out.d07.mode==='words'&&out.public_copy.lab===0&&out.public_copy.laboratoire===0&&out.offline.nav_ok&&out.offline.state&&out.offline.state.version==='132';
  return out;
}
async function testLetters(browser,spec){
  const x=await commonStart(browser,spec), p=x.page;
  const out={http_status:x.http_status,sw:x.sw,idb:x.idb,errors:x.errors};
  try{await p.waitForFunction(()=>typeof CORPUS!=='undefined'&&CORPUS.length>0,{timeout:30000});}catch(e){out.corpus_wait_error=String(e);}
  out.identity=await p.evaluate(()=>({version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,corpus:typeof CORPUS!=='undefined'?CORPUS.length:null,letters:document.querySelectorAll('.letter-item').length,role:document.getElementById('p-list')?.getAttribute('role'),label:document.getElementById('p-list')?.getAttribute('aria-label')}));
  try{
    out.help_focus=await p.evaluate(async()=>{
      try{ if(document.getElementById('help-modal')?.getAttribute('aria-hidden')==='false') closeHelp(true); }catch(_){}
      const opener=document.getElementById('snav-help') || document.getElementById('settings-help-btn') || document.querySelector('.phone-help-entry');
      if(!opener) return {error:'no help opener'};
      opener.focus();
      const before=document.activeElement===opener;
      openHelp('navigation',opener);
      await new Promise(r=>setTimeout(r,80));
      const opened={active:document.activeElement?.id,hidden:document.getElementById('help-modal')?.getAttribute('aria-hidden')};
      closeHelp(false);
      await new Promise(r=>setTimeout(r,80));
      return {before,opened,returned:document.activeElement===opener,active:document.activeElement?.id,hidden:document.getElementById('help-modal')?.getAttribute('aria-hidden')};
    });
  }catch(e){out.help_error=String(e);}
  await p.emulateMedia({forcedColors:'active'});
  out.forced=await p.evaluate(()=>{const e=document.querySelector('.ldj-card')||document.querySelector('.help-nav-btn.primary');if(!e)return null;const c=getComputedStyle(e);return{width:c.borderWidth,style:c.borderStyle};});
  out.offline=await offlineCold(x.context,spec.url,async q=>{try{await q.waitForFunction(()=>typeof CORPUS!=='undefined'&&CORPUS.length>0,{timeout:12000});}catch(e){}return q.evaluate(()=>({version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,corpus:typeof CORPUS!=='undefined'?CORPUS.length:null,letters:document.querySelectorAll('.letter-item').length}));});
  await p.close();await x.context.close();
  out.pass=out.http_status===200&&out.idb.pass&&out.sw.active&&out.identity.version==='2.10'&&out.identity.corpus>0&&out.identity.role==='main'&&out.help_focus&&out.help_focus.returned&&out.offline.nav_ok&&out.offline.state&&out.offline.state.version==='2.10'&&out.offline.state.corpus>0;
  return out;
}
(async()=>{
  for(const s of specs) report.served_byte_parity[s.key]=await servedParity(s);
  const browser=await chromium.launch({headless:true});
  report.apps['24H']=await test24(browser,specs[0]);
  report.apps['LDC']=await testLDC(browser,specs[1]);
  report.apps['Lettres']=await testLetters(browser,specs[2]);
  await browser.close();
  report.overall=Object.values(report.served_byte_parity).every(x=>x.pass)&&Object.values(report.apps).every(x=>x.pass)?'PASS':'FAIL';
  fs.writeFileSync('real-origin-final-prephysical-results.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  if(report.overall!=='PASS') process.exitCode=1;
})().catch(e=>{report.overall='HARNESS_ERROR';report.harness_error=String(e&&e.stack||e);fs.writeFileSync('real-origin-final-prephysical-results.json',JSON.stringify(report,null,2)+'\n');console.error(e);process.exitCode=2;});
