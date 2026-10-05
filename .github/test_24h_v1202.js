const { chromium } = require('playwright');
const fs = require('fs');
const BASE='http://127.0.0.1:8765/24h-v120-2-b1-core-loop-closure/';
const cases=[
  {name:'phone-light',viewport:{width:390,height:844},colorScheme:'light'},
  {name:'phone-dark',viewport:{width:390,height:844},colorScheme:'dark'},
  {name:'tablet-light',viewport:{width:820,height:1180},colorScheme:'light'},
  {name:'tablet-dark',viewport:{width:820,height:1180},colorScheme:'dark'}
];
const out={candidate:'v120.2/B1',cases:[],errors:[]};
function assert(v,msg){ if(!v) throw new Error(msg); }
async function settle(page){
  await page.waitForLoadState('domcontentloaded');
  await page.waitForFunction(()=>typeof state!=='undefined' && state && state.view==='home',{timeout:15000});
}
async function openFirst(page){
  const start=page.locator('.onboarding-primary');
  await start.waitFor({state:'visible'});
  await start.click();
  await page.waitForFunction(()=>state.view==='reader' && state.currentHour===1);
}
async function tabTo(page,selector,max=60){
  for(let i=0;i<max;i++){
    const active=await page.evaluate(sel=>document.activeElement && document.activeElement.matches(sel),selector);
    if(active) return i;
    await page.keyboard.press('Tab');
  }
  throw new Error('Could not keyboard-focus '+selector);
}
async function runCase(browser,cfg){
  const context=await browser.newContext({viewport:cfg.viewport,colorScheme:cfg.colorScheme});
  const page=await context.newPage();
  const errs=[]; page.on('pageerror',e=>errs.push('page:'+e.message)); page.on('console',m=>{if(m.type()==='error') errs.push('console:'+m.text())});
  const rec={name:cfg.name,checks:{}};
  try{
    await page.goto(BASE,{waitUntil:'domcontentloaded'}); await settle(page); await openFirst(page);
    rec.checks.old_prompt_absent=(await page.locator('text=Vous avez déjà médité cette Heure ?').count())===0;
    rec.checks.top_status=(await page.locator('[data-meditee-status-title-hour="1"]').innerText()).trim();
    assert(rec.checks.top_status==='Statut de l’Heure','top status');
    const recovery='[data-meditee-action-hour="1"][data-meditee-role="recovery"]';
    await tabTo(page,recovery);
    await page.keyboard.press('Shift+Tab');
    await page.keyboard.press('Tab');
    const focus=await page.locator(recovery).evaluate(el=>{const s=getComputedStyle(el);return {style:s.outlineStyle,width:s.outlineWidth,color:s.outlineColor,focusVisible:el.matches(':focus-visible'),active:document.activeElement===el}});
    rec.checks.recovery_focus=focus;
    assert(focus.active && focus.focusVisible && focus.style!=='none' && parseFloat(focus.width)>=3,'recovery focus ring');

    const end=page.locator('[data-meditee-action-hour="1"][data-meditee-role="primary-end"]');
    await end.scrollIntoViewIfNeeded();
    assert((await end.innerText()).trim()==='J’ai médité cette Heure','end unmarked label');
    assert(await end.getAttribute('aria-pressed')==='false','end unmarked aria');
    const next=page.locator('[data-meditee-next-hour="1"]');
    assert((await next.locator('[data-meditee-next-label]').innerText()).trim()==='Continuer sans marquer','unmarked next label');
    await next.click();
    await page.waitForFunction(()=>state.currentHour===2);
    rec.checks.forward_without_mark=await page.evaluate(()=>({currentHour:state.currentHour,h1:state.readHours.has(1),count:state.readHours.size}));
    assert(!rec.checks.forward_without_mark.h1,'forward mutated meditation state');

    await page.goto(BASE,{waitUntil:'domcontentloaded'}); await settle(page);
    await page.evaluate(()=>{ state.readHours.delete(1); });
    await page.evaluate(()=>openHour(1,false));
    await page.waitForFunction(()=>state.view==='reader' && state.currentHour===1);
    const end2=page.locator('[data-meditee-action-hour="1"][data-meditee-role="primary-end"]');
    await end2.scrollIntoViewIfNeeded(); await end2.focus(); await end2.click();
    await page.waitForFunction(()=>state.readHours.has(1) && document.querySelector('[data-meditee-role="primary-end"]').getAttribute('aria-pressed')==='true');
    rec.checks.marked={
      endText:(await end2.innerText()).trim(),
      top:(await page.locator('[data-meditee-status-title-hour="1"]').innerText()).trim(),
      next:(await page.locator('[data-meditee-next-hour="1"] [data-meditee-next-label]').innerText()).trim(),
      activeRole:await page.evaluate(()=>document.activeElement && document.activeElement.getAttribute('data-meditee-role'))
    };
    assert(rec.checks.marked.endText==='✓ Heure méditée — Retirer','marked button label');
    assert(rec.checks.marked.top==='✓ Heure méditée','top marked status');
    assert(rec.checks.marked.next==='Prier la 2e Heure','marked next label');
    assert(rec.checks.marked.activeRole==='primary-end','focus not retained on end action');
    await page.waitForTimeout(300);
    await page.reload({waitUntil:'domcontentloaded'}); await settle(page);
    rec.checks.persisted=await page.evaluate(()=>state.readHours.has(1));
    assert(rec.checks.persisted,'marked state not durable after reload');
    await page.evaluate(()=>openHour(1,false));
    await page.locator('[data-meditee-next-hour="1"]').click();
    await page.waitForFunction(()=>state.currentHour===2);
    rec.checks.marked_forward=await page.evaluate(()=>({currentHour:state.currentHour,h1:state.readHours.has(1)}));
    assert(rec.checks.marked_forward.h1,'marked state lost on forward');

    await page.evaluate(()=>openHour(24,false));
    await page.waitForFunction(()=>state.currentHour===24);
    rec.checks.hour24={
      end:await page.locator('[data-meditee-action-hour="24"][data-meditee-role="primary-end"]').count(),
      next:await page.locator('[data-meditee-next-hour="24"]').count()
    };
    assert(rec.checks.hour24.end===1 && rec.checks.hour24.next===0,'hour24 terminal regression');
    rec.checks.overflow=await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1);
    assert(rec.checks.overflow,'horizontal overflow');
    rec.checks.errors=errs; assert(errs.length===0,'runtime errors: '+errs.join(' | '));
    rec.status='PASS';
  }catch(e){rec.status='FAIL';rec.failure=e.message;out.errors.push(cfg.name+': '+e.message);}
  await context.close(); out.cases.push(rec);
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  for(const cfg of cases) await runCase(browser,cfg);
  await browser.close();
  out.status=out.errors.length?'FAIL':'PASS';
  fs.mkdirSync('qualification-24h-v120-2-b1',{recursive:true});
  fs.writeFileSync('qualification-24h-v120-2-b1/TARGETED_RUNTIME.json',JSON.stringify(out,null,2)+'\n');
  console.log(JSON.stringify(out,null,2));
  if(out.status!=='PASS') process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
