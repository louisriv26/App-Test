const { chromium } = require('playwright');
const fs = require('fs');

const ROOT = 'marie-v48-b3-csp-note-placeholder-closure';
const BASE = 'http://127.0.0.1:8080/' + ROOT + '/';

function parseColor(s) {
  const m = String(s).match(/rgba?\(([^)]+)\)/);
  if (!m) return null;
  const a = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
  return {r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]};
}
function composite(fg,bg) {
  const ba=bg.a===undefined?1:bg.a, a=fg.a+ba*(1-fg.a);
  return {r:(fg.r*fg.a+bg.r*ba*(1-fg.a))/a,g:(fg.g*fg.a+bg.g*ba*(1-fg.a))/a,b:(fg.b*fg.a+bg.b*ba*(1-fg.a))/a,a};
}
function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
function lum(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}
function contrast(a,b){return (Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05)}

async function ready(p) {
  await p.waitForFunction(() => {
    const l=document.getElementById('screen-loading');
    const mv=document.getElementById('mobile-version');
    return typeof APP_VERSION!=='undefined' && APP_VERSION==='48' &&
      typeof State!=='undefined' && Array.isArray(State.corpus) && State.corpus.length===37 &&
      l && !l.classList.contains('active') && mv && mv.textContent==='v48';
  }, null, {timeout:30000});
}
async function pseudoContrast(p, sel) {
  return p.$eval(sel, el => {
    function pc(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}}
    function comp(fg,bg){const ba=bg.a===undefined?1:bg.a,a=fg.a+ba*(1-fg.a);return{r:(fg.r*fg.a+bg.r*ba*(1-fg.a))/a,g:(fg.g*fg.a+bg.g*ba*(1-fg.a))/a,b:(fg.b*fg.a+bg.b*ba*(1-fg.a))/a,a}}
    function ln(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
    function L(c){return .2126*ln(c.r)+.7152*ln(c.g)+.0722*ln(c.b)}
    function R(a,b){return (Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
    const cs=getComputedStyle(el), ps=getComputedStyle(el,'::placeholder');
    let bg=pc(cs.backgroundColor)||{r:255,g:255,b:255,a:1};
    let q=el.parentElement;
    while(bg.a<1 && q){const b=pc(getComputedStyle(q).backgroundColor);if(b&&b.a>0)bg=comp(bg,b);q=q.parentElement}
    if(bg.a<1)bg=comp(bg,{r:255,g:255,b:255,a:1});
    const fg=pc(ps.color); if(!fg)return {selector:el.id||String(el.className||""),ratio:null,color:ps.color,bg:cs.backgroundColor};
    fg.a*=Number(ps.opacity||1);
    const rendered=comp(fg,bg);
    return {selector:el.id||String(el.className||""),ratio:R(rendered,bg),color:ps.color,opacity:ps.opacity,bg:cs.backgroundColor};
  });
}
async function elementContrast(p, sel, pseudo=null) {
  return p.$eval(sel, (el,pseudo) => {
    function pc(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}}
    function comp(fg,bg){const ba=bg.a===undefined?1:bg.a,a=fg.a+ba*(1-fg.a);return{r:(fg.r*fg.a+bg.r*ba*(1-fg.a))/a,g:(fg.g*fg.a+bg.g*ba*(1-fg.a))/a,b:(fg.b*fg.a+bg.b*ba*(1-fg.a))/a,a}}
    function ln(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
    function L(c){return .2126*ln(c.r)+.7152*ln(c.g)+.0722*ln(c.b)}
    function R(a,b){return (Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
    const cs=getComputedStyle(el,pseudo);
    let bg=pc(getComputedStyle(el).backgroundColor)||{r:0,g:0,b:0,a:0};
    let q=el.parentElement;
    while(bg.a<1 && q){const b=pc(getComputedStyle(q).backgroundColor);if(b&&b.a>0)bg=comp(bg,b);q=q.parentElement}
    if(bg.a<1)bg=comp(bg,{r:255,g:255,b:255,a:1});
    const fg=pc(cs.color); if(!fg)return null; fg.a*=Number(cs.opacity||1);
    return {ratio:R(comp(fg,bg),bg),color:cs.color,bg:getComputedStyle(el).backgroundColor};
  }, pseudo);
}

(async()=>{
  const browser=await chromium.launch({headless:true});
  const scenes=[];
  const viewports=[
    {name:'narrow',width:320,height:700,wide:false},
    {name:'iphone',width:390,height:844,wide:false},
    {name:'ipad',width:820,height:1180,wide:true},
  ];
  for(const vp of viewports){
    for(const mode of ['light','dark','system']){
      const ctx=await browser.newContext({
        viewport:{width:vp.width,height:vp.height},
        colorScheme:mode==='light'?'light':'dark'
      });
      await ctx.addInitScript(mode=>{
        localStorage.setItem('mjv_onboarded','1');
        if(mode==='system')localStorage.removeItem('mjv_theme');
        else localStorage.setItem('mjv_theme',mode);
      },mode);
      const p=await ctx.newPage();
      const pageErrors=[],consoleErrors=[];
      p.on('pageerror',e=>pageErrors.push(String(e)));
      p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
      const res=await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});
      await ready(p);
      const init=await p.evaluate(()=>({
        version:APP_VERSION,
        corpus:State.corpus.length,
        loadingActive:document.getElementById('screen-loading').classList.contains('active'),
        mobileVersion:document.getElementById('mobile-version').textContent,
        desktopVersion:document.getElementById('desktop-version').textContent,
        theme:document.documentElement.getAttribute('data-theme'),
        self:App.selfTest(),
        scrollWidth:document.documentElement.scrollWidth,
        clientWidth:document.documentElement.clientWidth,
      }));
      if(init.version!=='48'||init.corpus!==37||init.loadingActive||init.mobileVersion!=='v48'||init.desktopVersion!=='v48')
        throw new Error(vp.name+' '+mode+' readiness '+JSON.stringify(init));
      if(init.self.total!==156||init.self.passed!==156||init.self.failed.length)
        throw new Error(vp.name+' '+mode+' Pure suite '+JSON.stringify(init.self));
      if(init.scrollWidth>init.clientWidth+1)throw new Error(vp.name+' '+mode+' initial horizontal overflow');

      // Exercise real CSP event-dispatch paths and material journeys.
      if(!vp.wide){
        await p.click('#nav-search');
        await p.fill('#search-input','Fiat');
        await p.waitForSelector('#list-scroll .snippet-card',{timeout:10000});
        const ph=await pseudoContrast(p,'#search-input');
        if(ph.ratio<4.5)throw new Error(vp.name+' '+mode+' search placeholder contrast '+JSON.stringify(ph));
        await p.locator('#list-scroll .snippet-card').first().click();
        await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
        const body=await p.locator('#reader-body').innerText();
        if(body.trim().length<100)throw new Error(vp.name+' '+mode+' reader empty');
        const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
        if(!pid)throw new Error('missing reader pid');
        await p.evaluate(pid=>App.openNoteModal(pid),pid);
        await p.waitForSelector('#note-modal.open');
        const nph=await pseudoContrast(p,'#note-textarea');
        if(nph.ratio<4.5)throw new Error(vp.name+' '+mode+' note placeholder contrast '+JSON.stringify(nph));
        await p.click('#note-modal [data-csp-click="App.closeNoteModal()"]');
        await p.click('#reader-back-btn');
        await p.click('#nav-espace');
        await p.waitForSelector('#screen-espace.active .backup-btn.primary');
      } else {
        await p.click('#wnav-search');
        await p.fill('#wide-search-input','Fiat');
        await p.waitForSelector('#wide-list-scroll .snippet-card',{timeout:10000});
        const ph=await pseudoContrast(p,'#wide-search-input');
        if(ph.ratio<4.5)throw new Error(vp.name+' '+mode+' wide search placeholder contrast '+JSON.stringify(ph));
        await p.locator('#wide-list-scroll .snippet-card').first().click();
        await p.waitForFunction(()=>document.getElementById('wide-reader-content').style.display!=='none');
        const body=await p.locator('#wide-reader-body').innerText();
        if(body.trim().length<100)throw new Error(vp.name+' '+mode+' wide reader empty');
        const pid=await p.locator('#wide-reader-body p[data-pid]').first().getAttribute('data-pid');
        await p.evaluate(pid=>App.openNoteModal(pid),pid);
        await p.waitForSelector('#note-modal.open');
        const nph=await pseudoContrast(p,'#note-textarea');
        if(nph.ratio<4.5)throw new Error(vp.name+' '+mode+' note placeholder contrast '+JSON.stringify(nph));
        await p.click('#note-modal [data-csp-click="App.closeNoteModal()"]');
        await p.click('#wnav-espace');
        await p.waitForSelector('#wide-espace .backup-btn.primary');
      }

      // Preserve and re-check the v47 repaired dark-mode primary action treatment.
      if(mode!=='light'){
        const sel=vp.wide?'#wide-espace .backup-btn.primary':'#screen-espace .backup-btn.primary';
        const b=p.locator(sel).first();
        await b.hover();
        const hover=await elementContrast(p,sel);
        await b.focus();
        const focus=await elementContrast(p,sel);
        if(!hover||hover.ratio<4.5||!focus||focus.ratio<4.5)
          throw new Error(vp.name+' '+mode+' backup primary contrast '+JSON.stringify({hover,focus}));
      }

      // Help is another dynamically rendered CSP-controlled surface.
      if(!vp.wide){
        await p.evaluate(()=>App.openHelp());
        await p.waitForFunction(()=>document.getElementById('screen-aide').classList.contains('active'));
        if((await p.locator('#screen-aide').innerText()).trim().length<300)throw new Error('mobile help empty');
      } else {
        await p.click('#wnav-aide');
        await p.waitForSelector('#wide-aide');
        if((await p.locator('#wide-aide').innerText()).trim().length<300)throw new Error('wide help empty');
      }
      const end=await p.evaluate(()=>({
        scrollWidth:document.documentElement.scrollWidth,
        clientWidth:document.documentElement.clientWidth,
        visibleLoading:document.getElementById('screen-loading').classList.contains('active'),
        version:document.getElementById('mobile-version').textContent,
      }));
      if(end.scrollWidth>end.clientWidth+1)throw new Error(vp.name+' '+mode+' final horizontal overflow '+JSON.stringify(end));
      const qualifyingConsole=consoleErrors.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));
      if(pageErrors.length||qualifyingConsole.length)throw new Error(vp.name+' '+mode+' runtime errors '+JSON.stringify({pageErrors,qualifyingConsole}));
      scenes.push({viewport:vp.name,mode,http:res.status(),init,end,pageErrors,consoleErrors});
      await ctx.close();
    }
  }

  // Fresh persistence journey on the exact candidate using real controls.
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  await ctx.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
  let p=await ctx.newPage(); const pe=[],ce=[];
  p.on('pageerror',e=>pe.push(String(e)));p.on('console',m=>{if(m.type()==='error')ce.push(m.text())});
  await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});await ready(p);
  await p.click('.cal-cell[data-day="1"]');
  await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
  const unit=await p.evaluate(()=>currentUnit().unit_id);
  await p.click('#btn-complete');
  await p.click('#btn-activate');
  await p.click('#btn-textsize'); await p.click('#textsize-panel .textsize-option[data-text-level="xlarge"]');
  const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
  const notePara=p.locator('#reader-body p[data-pid]').first();
  await notePara.hover();
  const noteBtn=p.locator('#reader-body .para-note-btn').first();
  const notePointer=await noteBtn.evaluate(el=>getComputedStyle(el).pointerEvents);
  if(notePointer!=='auto')throw new Error('fine-pointer note control did not activate on paragraph hover: '+notePointer);
  await noteBtn.click();
  await p.fill('#note-textarea','QA_MARIE_V48_B3_NOTE_SENTINEL');
  await p.click('#note-modal .modal-btn-save');
  await p.waitForFunction(()=>Object.values(State.notes).some(n=>n.text==='QA_MARIE_V48_B3_NOTE_SENTINEL'),null,{timeout:10000});
  const envelope=await p.evaluate(()=>{
    const e=App.buildBackupEnvelope(new Date().toISOString());
    const v=Pure.validateBackupEnvelope(e,App.backupValidationContext());
    return {ok:v.ok,errors:v.errors||[],schema:e.schema_version||e.schemaVersion||null};
  });
  if(!envelope.ok)throw new Error('backup envelope validation '+JSON.stringify(envelope));
  const before=await p.evaluate(unit=>({
    unit,read:State.read.has(unit),activeDay:State.activeDay,textSize:State.textSize,
    note:Object.values(State.notes).some(n=>n.text==='QA_MARIE_V48_B3_NOTE_SENTINEL'),
    theme:localStorage.getItem('mjv_theme')
  }),unit);
  if(!before.read||before.activeDay!==1||before.textSize!=='xlarge'||!before.note||before.theme!=='dark')throw new Error('persistence setup '+JSON.stringify(before));
  await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p);
  const after=await p.evaluate(unit=>({
    read:State.read.has(unit),activeDay:State.activeDay,textSize:State.textSize,
    note:Object.values(State.notes).some(n=>n.text==='QA_MARIE_V48_B3_NOTE_SENTINEL'),
    theme:localStorage.getItem('mjv_theme')
  }),unit);
  if(!after.read||after.activeDay!==1||after.textSize!=='xlarge'||!after.note||after.theme!=='dark')throw new Error('persistence reload '+JSON.stringify(after));
  const qce=ce.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));
  if(pe.length||qce.length)throw new Error('persistence runtime errors '+JSON.stringify({pe,qce}));
  await ctx.close();

  await browser.close();
  const report={candidate:'MJV v48/B3',scenes,persistence:{before,after,envelope},status:'PASS'};
  fs.writeFileSync('MJV_v48_B3_RUNTIME_QA_EVIDENCE.json',JSON.stringify(report,null,2));
  console.log('MARIE_V48_B3_FULL_RUNTIME_PASS',scenes.length);
})().catch(e=>{console.error(e);process.exit(2)});