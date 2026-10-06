const { chromium, webkit } = require('playwright');
const fs=require('fs');
const BASE='http://127.0.0.1:8131/marie-v51-1-test/';
const results=[];
function assert(c,m){if(!c)throw new Error(m)}
function pass(name,detail){results.push({name,status:'PASS',detail});console.log('PASS',name,JSON.stringify(detail??null))}
async function ready(p){
  await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='51.1'&&State?.corpus?.length===37&&!document.getElementById('screen-loading')?.classList.contains('active'),null,{timeout:30000});
}
async function errorsGuard(p,label){
  const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  return ()=>{const bad=errs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));assert(!bad.length,label+' runtime errors '+JSON.stringify(bad));pass(label+':runtime_errors',[])};
}
async function runEngine(bt,name){
  const b=await bt.launch();
  const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'light'});
  await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light')});
  const p=await c.newPage(), done=await errorsGuard(p,name);
  await p.goto(BASE,{waitUntil:'domcontentloaded'}); await ready(p);

  const self=await p.evaluate(()=>App.selfTest()); assert(self.failed.length===0&&self.passed===self.total,'selfTest '+JSON.stringify(self)); pass(name+':selftest',self.total);

  // Mobile panel opens into its active option.
  const mt=p.locator('.mobile-textsize-trigger:visible').first();
  await mt.click(); await p.waitForSelector('#textsize-panel.open');
  let x=await p.evaluate(()=>({inside:document.getElementById('textsize-panel').contains(document.activeElement),active:document.activeElement?.textContent?.trim()}));
  assert(x.inside,'mobile panel did not receive focus '+JSON.stringify(x)); pass(name+':mobile_textsize_focus',x);

  // Mobile -> wide layout flip closes stale panels and moves focus to visible Aᵃ.
  await p.setViewportSize({width:1024,height:768});
  await p.waitForFunction(()=>window.matchMedia('(min-width: 768px) and (min-height: 600px)').matches&&State.lastWide===true);
  await p.waitForTimeout(180);
  x=await p.evaluate(()=>({
    mobileOpen:document.getElementById('textsize-panel').classList.contains('open'),
    wideOpen:document.getElementById('wide-textsize-panel').classList.contains('open'),
    activeId:document.activeElement?.id,
    activeVisible:document.activeElement?.getClientRects().length>0
  }));
  assert(!x.mobileOpen&&!x.wideOpen&&x.activeId==='wnav-textsize'&&x.activeVisible,'mobile->wide focus closure '+JSON.stringify(x));
  await p.keyboard.press('Tab');
  let after=await p.evaluate(()=>({id:document.activeElement?.id,visible:document.activeElement?.getClientRects().length>0}));
  assert(after.visible&&after.id!=='wnav-textsize','Tab trapped after mobile->wide '+JSON.stringify(after));
  pass(name+':mobile_to_wide', {flip:x,afterTab:after});

  // Wide panel opens into selected option.
  await p.locator('#wnav-textsize').click(); await p.waitForSelector('#wide-textsize-panel.open');
  await p.waitForFunction(()=>document.getElementById('wide-textsize-panel').contains(document.activeElement),null,{timeout:1500});
  x=await p.evaluate(()=>({inside:document.getElementById('wide-textsize-panel').contains(document.activeElement),active:document.activeElement?.textContent?.trim()}));
  assert(x.inside,'wide panel did not receive focus '+JSON.stringify(x));

  // Wide -> mobile layout flip closes stale panels and moves focus to visible mobile Aᵃ.
  await p.setViewportSize({width:390,height:844});
  await p.waitForFunction(()=>!window.matchMedia('(min-width: 768px) and (min-height: 600px)').matches&&State.lastWide===false);
  await p.waitForTimeout(180);
  x=await p.evaluate(()=>({
    mobileOpen:document.getElementById('textsize-panel').classList.contains('open'),
    wideOpen:document.getElementById('wide-textsize-panel').classList.contains('open'),
    mobileTrigger:document.activeElement?.classList?.contains('mobile-textsize-trigger')||false,
    activeVisible:document.activeElement?.getClientRects().length>0
  }));
  assert(!x.mobileOpen&&!x.wideOpen&&x.mobileTrigger&&x.activeVisible,'wide->mobile focus closure '+JSON.stringify(x));
  const beforeTab=await p.evaluate(()=>document.activeElement);
  await p.keyboard.press('Tab');
  after=await p.evaluate(()=>({cls:document.activeElement?.className,visible:document.activeElement?.getClientRects().length>0}));
  assert(after.visible,'Tab trapped after wide->mobile '+JSON.stringify(after));
  pass(name+':wide_to_mobile',{flip:x,afterTab:after});

  // Defensive stale hidden .open panel must not trap Tab.
  await p.evaluate(()=>{
    const hidden=document.getElementById('wide-textsize-panel'); hidden.classList.add('open');
    const t=Array.from(document.querySelectorAll('.mobile-textsize-trigger')).find(el=>el.getClientRects().length); t.focus();
    window.__qaStaleBefore=document.activeElement;
  });
  await p.keyboard.press('Tab');
  x=await p.evaluate(()=>({same:document.activeElement===window.__qaStaleBefore,visible:document.activeElement?.getClientRects().length>0}));
  assert(!x.same&&x.visible,'hidden stale panel trapped Tab '+JSON.stringify(x));
  await p.evaluate(()=>document.getElementById('wide-textsize-panel').classList.remove('open'));
  pass(name+':hidden_stale_panel_ignored',x);

  // B3: same worker version must not show banner; future version must show it even on first-load logic.
  await p.evaluate(()=>{document.getElementById('update-banner')?.remove();navigator.serviceWorker.dispatchEvent(new MessageEvent('message',{data:{type:'SW_UPDATED',version:'51.1'}}));});
  await p.waitForTimeout(30); assert(await p.locator('#update-banner').count()===0,'same-version false banner');
  await p.evaluate(()=>navigator.serviceWorker.dispatchEvent(new MessageEvent('message',{data:{type:'SW_UPDATED',version:'51.2'}})));
  await p.waitForSelector('#update-banner');
  pass(name+':version_driven_update_banner',true);
  await p.evaluate(()=>document.getElementById('update-banner')?.remove());

  // M-12/F-04 runtime chain.
  await p.evaluate(()=>App.openDay(1)); await p.waitForTimeout(80);
  const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
  assert(pid,'no paragraph pid');
  const len=await p.evaluate(pid=>findPara(pid).para.text.length,pid);
  const end=Math.min(6,len);
  await p.evaluate(async ({pid,end})=>{await App.applyRangeHighlight(pid,0,end,'gold',findPara(pid).para.text.slice(0,end));},{pid,end});
  const count1=await p.evaluate(pid=>activeHlRecords(pid).length,pid);
  await p.locator(`#reader-body p[data-pid="${pid}"] mark[data-hlid]`).first().click();
  x=await p.evaluate(pid=>({picker:State.hlPickerPid,open:document.getElementById('hl-picker').classList.contains('open')}),pid);
  assert(x.picker===pid&&x.open,'highlight click picker failed '+JSON.stringify(x));
  await p.evaluate(()=>App.closeHlPicker());
  await p.evaluate(async ({pid,end})=>{await App.applyRangeHighlight(pid,Math.max(1,end-2),Math.min(end+2,findPara(pid).para.text.length),'blue','overlap');},{pid,end});
  const count2=await p.evaluate(pid=>activeHlRecords(pid).length,pid);
  assert(count2===count1,'overlap was persisted '+count1+'->'+count2);
  pass(name+':highlight_click_and_overlap',{count1,count2});

  // M-16/M-15 initial destructive focus + truthful consequence text.
  await p.evaluate(()=>App.startNewCycle()); await p.waitForSelector('#cycle-reset-modal.open');
  x=await p.evaluate(()=>({focus:document.activeElement?.textContent?.trim(),text:document.getElementById('cycle-reset-modal').innerText}));
  assert(x.focus==='Annuler','cycle reset initial focus '+JSON.stringify(x));
  assert(/pratique active/i.test(x.text)&&/positions de lecture/i.test(x.text),'cycle reset wording '+x.text);
  await p.evaluate(()=>App.closeCycleResetModal());
  pass(name+':cycle_reset_safety',x.focus);

  // M-19 accessible names after opening day 2.
  await p.evaluate(()=>App.openDay(2)); await p.waitForTimeout(50);
  x=await p.evaluate(()=>({
    prevVisible:document.getElementById('reader-prev-label').textContent.trim(),
    prevAria:document.getElementById('reader-prev').getAttribute('aria-label'),
    actVisible:document.getElementById('reader-activate-label').textContent.trim(),
    actAria:document.getElementById('reader-btn-activate').getAttribute('aria-label')
  }));
  assert(x.prevAria.startsWith(x.prevVisible),'prev Label-in-Name '+JSON.stringify(x));
  assert(x.actAria.startsWith(x.actVisible),'activate Label-in-Name '+JSON.stringify(x));
  pass(name+':label_in_name',x);

  // Wide focus and heading semantics + v50 today-card protected geometry.
  await p.setViewportSize({width:1024,height:768}); await p.waitForFunction(()=>State.lastWide===true); await p.waitForTimeout(120);
  await p.locator('#wnav-jours').focus();
  x=await p.evaluate(()=>{
    const b=document.getElementById('wnav-jours'),cs=getComputedStyle(b),top=getComputedStyle(document.getElementById('wide-topbar'));
    const card=getComputedStyle(document.getElementById('ws-today-card'));
    return {outline:cs.outlineColor,bg:top.backgroundColor,flex:card.flex,max:card.maxHeight,helpH1:!!document.querySelector('#wide-aide h1'),espaceH1:(()=>{App.renderEspace('wide-espace');return !!document.querySelector('#wide-espace h1')})()};
  });
  assert(x.outline!==x.bg,'wide focus invisible '+JSON.stringify(x));
  assert(x.flex==='1 1 auto'&&x.max==='none','v50 today-card regression '+JSON.stringify(x));
  assert(x.helpH1&&x.espaceH1,'wide heading regression '+JSON.stringify(x));
  pass(name+':wide_focus_headings_geometry',x);

  done(); await c.close(); await b.close();
}
(async()=>{
  await runEngine(chromium,'chromium');
  await runEngine(webkit,'webkit');
  fs.writeFileSync('/tmp/MARIE_v51_1_BROWSER_QA.json',JSON.stringify({status:'PASS',version:'51.1',results},null,2));
  console.log('MARIE_V51_1_BROWSER_QA_PASS',results.length);
})().catch(e=>{console.error('MARIE_V51_1_BROWSER_QA_FAIL',e);process.exit(2)});