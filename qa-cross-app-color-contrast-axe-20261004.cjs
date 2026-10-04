const { chromium } = require('playwright');
const axeSource = require('axe-core').source;
const fs=require('fs');
const BASE='http://127.0.0.1:8094/';
const APPS={
  lettres:{url:BASE+'lettres-r9/'},
  marie:{url:BASE+'marie-v48-test/'}
};

function summarizeAxe(r){
  return (r.violations||[]).filter(v=>v.id==='color-contrast').map(v=>({
    id:v.id,impact:v.impact,help:v.help,
    nodes:v.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))
  }));
}
async function axeContrast(p,label){
  const r=await p.evaluate(async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
  return {label,violations:summarizeAxe(r)};
}
async function errorsOn(p,errs){p.on('pageerror',e=>errs.push('PAGE '+String(e)));p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});}
async function waitLettres(p){await p.waitForFunction(()=>window.__LET_F_TEST&&typeof openTextBar==='function',{timeout:30000});}
async function waitMarie(p){await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='48'&&typeof State!=='undefined'&&Array.isArray(State.corpus)&&State.corpus.length===37&&document.getElementById('screen-loading')&&!document.getElementById('screen-loading').classList.contains('active'),{timeout:30000});}

async function lettresScenes(browser,viewport,theme){
  const c=await browser.newContext({viewport,colorScheme:theme});
  await c.addInitScript({content:axeSource});
  const p=await c.newPage(),errs=[];await errorsOn(p,errs);
  await p.goto(APPS.lettres.url,{waitUntil:'domcontentloaded',timeout:60000});await waitLettres(p);
  await p.evaluate(t=>setThemeFromSettings(t),theme);await p.waitForTimeout(150);
  const scenes=[];
  async function scan(label){scenes.push(await axeContrast(p,label));}
  for(const panel of ['p-home','p-list','p-search','p-notes','p-explore']){
    await p.evaluate(id=>switchPanel(id),panel);await p.waitForTimeout(100);await scan(panel);
  }
  await p.evaluate(()=>openTextBar());await p.waitForTimeout(100);await scan('settings');
  await p.evaluate(()=>openDeviceTransferFromSettings());await p.waitForTimeout(100);await scan('transfer');
  await p.evaluate(()=>{try{closeDeviceTransfer()}catch(e){};try{closeTextBar()}catch(e){}});await p.waitForTimeout(80);
  await p.evaluate(()=>openHelp('navigation',document.body));await p.waitForTimeout(100);await scan('help');
  await p.evaluate(()=>{try{closeHelp()}catch(e){}});await p.waitForTimeout(80);
  // Reader: first letter via list.
  await p.evaluate(()=>switchPanel('p-list'));await p.waitForTimeout(100);
  const first=p.locator('.letter-item').first();if(await first.count()){await first.click();await p.waitForTimeout(150);await scan('reader');}
  return {viewport,theme,scenes,errors:errs};
}

async function marieScenes(browser,viewport,theme){
  const c=await browser.newContext({viewport,colorScheme:theme});
  await c.addInitScript({content:axeSource});
  const p=await c.newPage(),errs=[];await errorsOn(p,errs);
  // Preserve first-run onboarding for one scan, but preselect theme.
  await p.addInitScript(t=>{localStorage.removeItem('mjv_onboarded');localStorage.setItem('mjv_theme',t)},theme);
  await p.goto(APPS.marie.url,{waitUntil:'domcontentloaded',timeout:60000});await waitMarie(p);
  const scenes=[];
  async function scan(label){scenes.push(await axeContrast(p,label));}
  if(await p.locator('#onboard-modal.open').count()) await scan('onboarding');
  await p.evaluate(async t=>{if(typeof App!=='undefined'&&App.applyTheme)await App.applyTheme(t)},theme);await p.waitForTimeout(120);
  await p.evaluate(async()=>{if(document.getElementById('onboard-modal')?.classList.contains('open')) await App.finishOnboarding()});await p.waitForTimeout(120);
  await scan('home');
  const wide=viewport.width>=768 && viewport.height>=480;
  if(wide){
    await p.evaluate(()=>App.wideNav('search'));await p.waitForTimeout(80);
    const inp=p.locator('#wide-search-input');if(await inp.count()){await inp.fill('Fiat');await p.waitForTimeout(180);}await scan('search');
    const res=p.locator('#wide-list-scroll .snippet-card').first();if(await res.count()){await res.click();await p.waitForTimeout(180);await scan('reader');}
    await p.evaluate(()=>App.wideNav('espace'));await p.waitForTimeout(120);await scan('espace');
    await p.evaluate(()=>App.toggleWideTextsizePanel());await p.waitForTimeout(100);await scan('textsize');
    await p.evaluate(()=>App.openThemePicker(document.getElementById('wnav-dark')));await p.waitForTimeout(100);await scan('theme-picker');
    await p.evaluate(()=>App.closeThemePicker());await p.waitForTimeout(50);
    await p.evaluate(()=>App.openHelp());await p.waitForTimeout(120);await scan('help');
  } else {
    await p.evaluate(()=>App.openSearchNav());await p.waitForTimeout(80);
    const inp=p.locator('#search-input');if(await inp.count()){await inp.fill('Fiat');await p.waitForTimeout(180);}await scan('search');
    const res=p.locator('#list-scroll .snippet-card').first();if(await res.count()){await res.click();await p.waitForTimeout(180);await scan('reader');
      const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');if(pid){await p.evaluate(pid=>App.openNoteModal(pid),pid);await p.waitForTimeout(100);await scan('note-modal');await p.evaluate(()=>App.closeNoteModal());await p.waitForTimeout(50);}
    }
    await p.evaluate(()=>App.showScreen('espace'));await p.waitForTimeout(120);await scan('espace');
    await p.evaluate(()=>App.toggleTextsizePanel());await p.waitForTimeout(100);await scan('textsize');
    await p.evaluate(()=>App.openThemePicker(document.getElementById('dark-toggle-btn')));await p.waitForTimeout(100);await scan('theme-picker');
    await p.evaluate(()=>App.closeThemePicker());await p.waitForTimeout(50);
    await p.evaluate(()=>App.openHelp());await p.waitForTimeout(120);await scan('help');
  }
  return {viewport,theme,scenes,errors:errs};
}

(async()=>{
 const browser=await chromium.launch({headless:true});
 const out={lettres:[],marie:[],status:'FAIL'};
 const viewports=[{name:'phone',width:390,height:844},{name:'wide',width:820,height:1180},{name:'desktop',width:1535,height:959}];
 for(const theme of ['light','dark']){
   for(const vp of viewports){
     const v={width:vp.width,height:vp.height,name:vp.name};
     if(vp.name!=='wide') out.lettres.push(await lettresScenes(browser,v,theme));
     if(vp.name!=='desktop') out.marie.push(await marieScenes(browser,v,theme));
   }
 }
 await browser.close();
 out.status='PASS_EXECUTION';
 fs.writeFileSync('CROSS_APP_RENDERED_COLOR_CONTRAST_AUDIT_2026-10-04.json',JSON.stringify(out,null,2));
 const compact={};
 for(const app of ['lettres','marie']){
   compact[app]=[];
   for(const run of out[app]) for(const sc of run.scenes) if(sc.violations.length) compact[app].push({viewport:run.viewport.name,theme:run.theme,scene:sc.label,violations:sc.violations});
 }
 console.log(JSON.stringify(compact,null,2));
})().catch(e=>{console.error(e);process.exit(2)});