const { chromium }=require('playwright'); const fs=require('fs');
const U={
 h24:'https://louisriv26.github.io/App-Test/24h-v119-b1-prephysical/',
 ldc:'https://louisriv26.github.io/App-Test/ldc-v132-b1-prephysical/',
 lettres:'https://louisriv26.github.io/App-Test/lettres-v2.10-b1-prephysical/'
};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function lum(c){const m=String(c).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);if(!m)return null;const rgb=m.slice(1).map(Number).map(x=>x/255).map(x=>x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4));return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]}
function ratio(a,b){const A=lum(a),B=lum(b);if(A==null||B==null)return null;return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)}
async function open(page,url){await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});await sleep(900)}
(async()=>{
 const browser=await chromium.launch({headless:true});const R={apps:{},overall:'UNKNOWN'};
 try{
   // 24H normal context
   {
    const c=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'allow'}),p=await c.newPage();await open(p,U.h24);
    await p.evaluate(()=>openHour(1,false));await sleep(300);
    const tabs=await p.locator('[role=tab]').count();
    const start=await p.locator('[role=tab][aria-selected=true]').getAttribute('data-tab');
    await p.locator('[role=tab][aria-selected=true]').focus();await p.keyboard.press('ArrowRight');await sleep(80);
    const after={focus:await p.evaluate(()=>document.activeElement&&document.activeElement.getAttribute('data-tab')),selected:await p.locator('[role=tab][aria-selected=true]').getAttribute('data-tab'),hiddenMed:await p.locator('#meditationContent').getAttribute('aria-hidden')};
    // keyboard-tab reachability: start just before action using a nearby known control, then use keyboard only
    const focusRes=await p.evaluate(()=>{const b=document.querySelector('.mark-btn');if(!b)return {exists:false};b.tabIndex=0;const prev=b.previousElementSibling;if(prev&&prev.focus){prev.tabIndex=0;prev.focus();return {exists:true,prev:true}} document.body.focus();return {exists:true,prev:false}});
    let reached=false, outline=null, active=null;
    for(let i=0;i<80;i++){await p.keyboard.press('Tab');active=await p.evaluate(()=>document.activeElement&&document.activeElement.className||'');if(String(active).includes('mark-btn')){reached=true;outline=await p.locator('.mark-btn').evaluate(e=>({style:getComputedStyle(e).outlineStyle,width:getComputedStyle(e).outlineWidth,color:getComputedStyle(e).outlineColor}));break}}
    const noteName=await p.locator('#noteTextarea').getAttribute('aria-label');
    const dark=await p.evaluate(()=>{document.documentElement.setAttribute('data-theme','dark');const e=document.querySelector('.mark-btn:not(.done)')||document.querySelector('.mark-btn');const s=getComputedStyle(e);return {fg:s.color,bg:s.backgroundColor}});
    R.apps.h24={tabs,start,after,keyboard:{focusRes,reached,outline,active},noteName,dark,darkRatio:ratio(dark.fg,dark.bg)};
    R.apps.h24.pass=tabs===3&&start==='meditation'&&after.focus==='reflection'&&after.selected==='reflection'&&after.hiddenMed==='true'&&reached&&outline&&outline.style!=='none'&&parseFloat(outline.width)>=2&&noteName==='Note personnelle'&&R.apps.h24.darkRatio>=4.5;
    await c.close();
   }
   // 24H forced-colors context
   {
    const c=await browser.newContext({viewport:{width:390,height:844},forcedColors:'active'}),p=await c.newPage();await open(p,U.h24);
    R.apps.h24.forced=await p.evaluate(()=>{const out={};for(const sel of ['.bn-item','.mark-btn','.mark-read-btn']){const e=document.querySelector(sel);if(e){const s=getComputedStyle(e);out[sel]={borderWidth:s.borderTopWidth,borderStyle:s.borderTopStyle}}}return out});
    R.apps.h24.pass=R.apps.h24.pass&&Object.values(R.apps.h24.forced).length>=2&&Object.values(R.apps.h24.forced).every(x=>parseFloat(x.borderWidth)>=1&&x.borderStyle!=='none');
    await c.close();
   }
   // LDC
   {
    const c=await browser.newContext({viewport:{width:1180,height:850},serviceWorkers:'allow'}),p=await c.newPage();await open(p,U.ldc);
    const x=await p.evaluate(async()=>{localStorage.setItem('ldc_search_intent_mode_v3','meaning');loadSearchIntentMode();renderSearchIntentMode();const pf=await offlineStoragePreflight();return {mode:searchIntentMode,stored:localStorage.getItem('ldc_search_intent_mode_v3'),words:document.getElementById('search-intent-words').getAttribute('aria-pressed'),meaning:document.getElementById('search-intent-meaning').getAttribute('aria-pressed'),storage:pf,storageText:document.getElementById('offline-storage-detail').textContent,version:APP_VERSION,pub:PUBLIC_VERSION,copy:document.body.innerText};});
    R.apps.ldc=x;R.apps.ldc.pass=x.mode==='words'&&x.stored===null&&x.words==='true'&&x.meaning==='false'&&String(x.version)==='132'&&String(x.pub)==='132'&&x.storage&&x.storage.supported&&x.storage.quota>0&&x.storageText.startsWith('Stockage :')&&!/LAB interne/i.test(x.copy)&&!/laboratoire/i.test(x.copy);
    await c.close();
   }
   // Lettres normal + forced
   {
    const c=await browser.newContext({viewport:{width:1180,height:850}}),p=await c.newPage();await open(p,U.lettres);
    const normal=await p.evaluate(()=>({version:APP_VERSION,mainRole:document.getElementById('p-list').getAttribute('role'),mainLabel:document.getElementById('p-list').getAttribute('aria-label')}));
    await p.locator('#snav-help').focus();await p.locator('#snav-help').click();await sleep(80);await p.locator('#help-close-btn').click();await sleep(80);
    normal.focusReturned=await p.evaluate(()=>document.activeElement&&document.activeElement.id);
    R.apps.lettres={normal};await c.close();
    const cf=await browser.newContext({viewport:{width:390,height:844},forcedColors:'active'}),pf=await cf.newPage();await open(pf,U.lettres);
    R.apps.lettres.forced=await pf.evaluate(()=>{const candidates=['.chip.active','.snav-item.active','.setting-choice.active'];const out={};for(const sel of candidates){const e=document.querySelector(sel);if(e){const s=getComputedStyle(e);out[sel]={w:s.borderTopWidth,style:s.borderTopStyle}}}return out});await cf.close();
    R.apps.lettres.pass=normal.version==='2.10'&&normal.mainRole==='main'&&normal.mainLabel==='Liste des lettres'&&normal.focusReturned==='snav-help'&&Object.values(R.apps.lettres.forced).some(x=>parseFloat(x.w)>=2&&x.style!=='none');
   }
   R.overall=Object.values(R.apps).every(x=>x.pass)?'PASS':'FAIL';
 } finally{await browser.close()}
 fs.writeFileSync('changed-surface-a11y-final-prephysical-results.json',JSON.stringify(R,null,2)+'\n');console.log(JSON.stringify(R,null,2));if(R.overall!=='PASS')process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2});
