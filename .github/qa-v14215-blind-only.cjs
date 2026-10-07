const { chromium }=require('playwright'); const fs=require('fs');
const URL='https://louisriv26.github.io/App-Test/?blind='+Date.now();
const out={generated_at:new Date().toISOString(),candidate:'v2.19.142.15-R1B-RELEASE-TRUTH-SCOPE-CLOSURE',checks:{},findings:[],errors:[],overall:'UNKNOWN'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function ready(p){await p.waitForFunction(()=>{const l=document.getElementById('loading'),v=document.getElementById('version-pill-home');return !!(l&&getComputedStyle(l).display==='none'&&v&&v.textContent&&!/v—|v-$/.test(v.textContent));},null,{timeout:120000});await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none'&&typeof finishOnboarding==='function')finishOnboarding();});}
(async()=>{const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:320,height:640},serviceWorkers:'allow',colorScheme:'dark',locale:'fr-FR'});const p=await c.newPage();p.on('pageerror',e=>out.errors.push('page:'+String(e)));p.on('console',m=>{if(m.type()==='error')out.errors.push('console:'+m.text())});
try{
 const r=await p.goto(URL,{waitUntil:'domcontentloaded',timeout:120000});await ready(p);
 out.checks.identity=await p.evaluate(()=>APP_VERSION==='v2.19.142.15-R1B-RELEASE-TRUTH-SCOPE-CLOSURE'&&PUBLIC_VERSION==='142.15'&&SW_CACHE_VERSION==='ldc-v2.19.142.15-R1B-release-truth-scope-closure');
 out.checks.remote_http=(r&&r.status())===200;
 const rapid=await p.evaluate(async()=>{const a=[];await goSearch();for(let i=0;i<18;i++){const view=['enriched','aflp','additions'][i%3],m=i%2?'meaning':'words';await setSupplementMode(view,{persist:false,rerender:false,silent:true,origin:'blind'});setSearchIntentMode(m,{rerun:false,persist:false});renderSearchIntentMode();const n=document.getElementById('search-semantic-scope-note');a.push({view,m,hidden:n.hidden});}return a;});
 out.checks.e07_rapid=rapid.every(x=>x.hidden===!(x.m==='meaning'&&(x.view==='aflp'||x.view==='additions')));
 const focus=await p.evaluate(()=>{const trigger=document.getElementById('search-documentary-view-action')||document.getElementById('reader-supplement-mode-action');if(trigger)trigger.focus();openDocumentaryView();return{open:getComputedStyle(document.getElementById('documentary-view-overlay')).display!=='none',active:document.activeElement&&document.activeElement.id};});
 await p.keyboard.press('Escape');await sleep(120);const after=await p.evaluate(()=>({open:getComputedStyle(document.getElementById('documentary-view-overlay')).display!=='none',active:document.activeElement&&(document.activeElement.id||document.activeElement.tagName)}));
 out.checks.modal_escape=focus.open&&!after.open;out.findings.push({id:'E12_FOCUS',before:focus,after});
 await p.evaluate(()=>{applyTextLevel('xlarge');setSearchIntentMode('meaning',{rerun:false,persist:false});});
 const lay=await p.evaluate(()=>{const n=document.getElementById('search-semantic-scope-note'),r=n.getBoundingClientRect();return{inner:innerWidth,doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,note:{left:r.left,right:r.right,width:r.width,height:r.height}}});
 out.checks.hostile_layout=lay.doc<=lay.inner+1&&lay.body<=lay.inner+1&&lay.note.right<=lay.inner+1;out.findings.push({id:'LAYOUT_320_XL_DARK',lay});
 await p.evaluate(()=>{const t=document.getElementById('search-input-meaning');t.value='zxqv pizza nébuleuse 84917 banane';onSearchInput('meaning');});
 await p.evaluate(()=>runSearch());await p.waitForFunction(()=>document.getElementById('search-progress')?.textContent===''||getComputedStyle(document.getElementById('search-progress')).display==='none',null,{timeout:360000}).catch(()=>{});await sleep(700);
 const gib=await p.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,meta:document.getElementById('search-meta')?.textContent||'',confidence:searchLastPayload?.payload?.confidence||searchLastPayload?.confidence||null}));
 out.findings.push({id:'E04_GIBBERISH',severity:gib.cards>0?'material-search-quality':'none',gib});
 setTimeout(()=>{},0);
 await p.evaluate(()=>{setSearchIntentMode('words',{rerun:false,persist:false});const i=document.getElementById('search-input');i.value="Jésus explique que l'âme doit abandonner sa volonté humaine pour vivre entièrement dans la volonté divine";onSearchInput('words');});
 await p.evaluate(()=>runSearch());await sleep(1200);const lex=await p.evaluate(()=>({cards:document.querySelectorAll('#search-results .result-card').length,text:document.getElementById('search-results')?.innerText.slice(0,500)||'',lane:searchResultLane,expanded:searchPartialExpanded}));
 out.findings.push({id:'E20_LONG_LEXICAL_DESCRIPTION',lex});
 let invalid;try{invalid=await p.evaluate(async()=>{pendingParaId='THIS_DOES_NOT_EXIST';await openEntry(1,'THIS_ENTRY_DOES_NOT_EXIST','search');return{screen:document.querySelector('.screen.active')?.id,current:currentEntry&&currentEntry.id||null};});}catch(e){invalid={error:String(e)}}out.findings.push({id:'INVALID_TARGET',invalid});out.checks.invalid_target_no_crash=!!invalid;
 const env=await p.evaluate(async()=>{const reg=await navigator.serviceWorker.ready;const req=indexedDB.open('ldc_user_v1');return new Promise(res=>{req.onsuccess=()=>{req.result.close();res({origin:location.origin,scope:reg.scope,script:reg.active&&reg.active.scriptURL,db:'ldc_user_v1'});};req.onerror=()=>res({origin:location.origin,scope:reg.scope,db:'ldc_user_v1',error:String(req.error)});});});
 out.findings.push({id:'E16_E19_ENVIRONMENT',env});
 out.checks.no_page_errors=out.errors.length===0;
 out.overall=Object.values(out.checks).every(Boolean)?'PASS_WITH_FINDINGS':'FAIL';
}catch(e){out.errors.push(String(e&&e.stack||e));out.overall='HARNESS_ERROR'}finally{await c.close();await b.close();}
fs.writeFileSync('qa-v14215-blind-only-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));if(out.overall==='FAIL'||out.overall==='HARNESS_ERROR')process.exitCode=1;
})();