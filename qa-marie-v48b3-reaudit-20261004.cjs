const { chromium } = require('playwright');
const fs = require('fs');

const ROOT='qa-marie-v48b3-reaudit-package';
const BASE='http://127.0.0.1:8090/'+ROOT+'/';
const UPDATE_ROOT='qa-marie-v48b3-reaudit-update';
const UPDATE_BASE='http://127.0.0.1:8091/'+UPDATE_ROOT+'/';

function badErrors(xs){return xs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));}
async function ready(p,version='48'){
  await p.waitForFunction(v=>{
    const l=document.getElementById('screen-loading');
    const mv=document.getElementById('mobile-version');
    return typeof APP_VERSION!=='undefined' && APP_VERSION===v &&
      typeof State!=='undefined' && Array.isArray(State.corpus) && State.corpus.length===37 &&
      l && !l.classList.contains('active') && mv && mv.textContent==='v'+v;
  },version,{timeout:30000});
}
async function contrastFor(p,sel,pseudo=null){
  return await p.$eval(sel,(el,pseudo)=>{
    function pc(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}}
    function comp(f,b){const ba=b.a===undefined?1:b.a,a=f.a+ba*(1-f.a);return{r:(f.r*f.a+b.r*ba*(1-f.a))/a,g:(f.g*f.a+b.g*ba*(1-f.a))/a,b:(f.b*f.a+b.b*ba*(1-f.a))/a,a}}
    function ln(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
    function L(c){return .2126*ln(c.r)+.7152*ln(c.g)+.0722*ln(c.b)}
    function R(a,b){return (Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
    const cs=getComputedStyle(el,pseudo);
    let fg=pc(cs.color); if(!fg)return null; fg.a*=Number(cs.opacity||1);
    let bg=pc(getComputedStyle(el).backgroundColor)||{r:0,g:0,b:0,a:0},q=el.parentElement;
    while(bg.a<1&&q){const b=pc(getComputedStyle(q).backgroundColor);if(b&&b.a>0)bg=comp(bg,b);q=q.parentElement}
    if(bg.a<1)bg=comp(bg,{r:255,g:255,b:255,a:1});
    return {ratio:R(comp(fg,bg),bg),color:cs.color,background:getComputedStyle(el).backgroundColor,opacity:cs.opacity};
  },pseudo);
}
async function attachErrors(p,errors){
  p.on('pageerror',e=>errors.push('PAGE '+String(e)));
  p.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE '+m.text())});
}
async function assertCore(p,label){
  const x=await p.evaluate(()=>({
    version:APP_VERSION,
    corpus:State.corpus.length,
    loading:document.getElementById('screen-loading').classList.contains('active'),
    mv:document.getElementById('mobile-version').textContent,
    dv:document.getElementById('desktop-version').textContent,
    self:App.selfTest(),
    sw:!!navigator.serviceWorker,
    width:[document.documentElement.scrollWidth,document.documentElement.clientWidth]
  }));
  if(x.version!=='48'||x.corpus!==37||x.loading||x.mv!=='v48'||x.dv!=='v48') throw new Error(label+' readiness '+JSON.stringify(x));
  if(x.self.total!==156||x.self.passed!==156||x.self.failed.length) throw new Error(label+' selftest '+JSON.stringify(x.self));
  if(x.width[0]>x.width[1]+1) throw new Error(label+' horizontal overflow '+JSON.stringify(x.width));
  return x;
}

(async()=>{
  const browser=await chromium.launch({headless:true});
  const report={candidate:'MJV v48/B3 fresh re-audit',firstRun:null,mobile:null,android:null,wide:null,deepLinks:null,backupValidation:null,updateOffline:null,status:'FAIL'};

  // 1. First-run system-dark onboarding -> Help, specifically challenge dark Help controls.
  {
    const c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    const p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    const core=await assertCore(p,'first-run');
    const ob=await p.locator('#onboard-modal').evaluate(el=>el.classList.contains('open'));
    if(!ob) throw new Error('first-run onboarding not open');
    const onboardText=await p.locator('#onboard-modal').innerText();
    if(!/31 jours \+ 6 appendices/.test(onboardText)) throw new Error('first-run onboarding content incomplete');
    await p.click('#onboard-aide-btn');
    await p.waitForFunction(()=>document.getElementById('screen-aide').classList.contains('active'));
    const onboarded=await p.evaluate(()=>localStorage.getItem('mjv_onboarded'));
    if(onboarded!=='1') throw new Error('onboarding marker not persisted');
    const navCount=await p.locator('#screen-aide .help-nav a').count();
    if(navCount<5) throw new Error('help nav missing topics '+navCount);
    const navRatios=[];
    for(let i=0;i<navCount;i++){
      const a=p.locator('#screen-aide .help-nav a').nth(i);
      const ratio=await a.evaluate(el=>{
        function h2r(h){const m=h.match(/rgba?\(([^)]+)\)/);const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return a.slice(0,3)}
        function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
        function lum(c){return .2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2])}
        const cs=getComputedStyle(el), fg=h2r(cs.color); let n=el,bg=null;
        while(n&&!bg){const c=getComputedStyle(n).backgroundColor;if(!/rgba?\(0,\s*0,\s*0,\s*0\)/.test(c)&&!c.includes('/ 0'))bg=h2r(c);n=n.parentElement}
        bg=bg||[26,23,32]; return (Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);
      });
      navRatios.push(ratio); if(ratio<4.5) throw new Error('dark help nav contrast '+ratio);
    }
    const summarySel='#screen-aide details.transfer-card > summary';
    await p.waitForSelector(summarySel);
    const arrow=await contrastFor(p,summarySel,'::after');
    if(!arrow||arrow.ratio<4.5) throw new Error('dark help disclosure arrow contrast '+JSON.stringify(arrow));
    await p.locator(summarySel).click();
    const open=await p.locator('#screen-aide details.transfer-card').first().evaluate(el=>el.open);
    if(!open) throw new Error('help disclosure did not open');
    const bad=badErrors(errors); if(bad.length) throw new Error('first-run runtime errors '+JSON.stringify(bad));
    report.firstRun={core,navCount,minNavContrast:Math.min(...navRatios),arrow,onboarded,errors};
    await c.close();
  }

  // 2. Mobile material journey + persistence + cycle reset preservation.
  {
    const c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
    let p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p); const core=await assertCore(p,'mobile');
    await p.click('#nav-search'); await p.fill('#search-input','Fiat'); await p.waitForSelector('#list-scroll .snippet-card');
    const results=await p.locator('#list-scroll .snippet-card').count(); if(results<1) throw new Error('mobile search no results');
    await p.locator('#list-scroll .snippet-card').first().click();
    await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
    const unit=await p.evaluate(()=>currentUnit().unit_id);
    await p.click('#btn-complete'); await p.waitForFunction(()=>State.read.size>0);
    await p.click('#btn-activate'); await p.waitForFunction(()=>State.activeDay!==null||State.activeAppendix!==null);
    await p.click('#btn-textsize'); await p.click('#textsize-panel .textsize-option[data-text-level="xlarge"]');
    const para=p.locator('#reader-body p[data-pid]').first(); await para.hover();
    const noteBtn=p.locator('#reader-body .para-note-btn').first(); await noteBtn.click();
    await p.fill('#note-textarea','FRESH_REAUDIT_NOTE');
    await p.click('#note-modal .modal-btn-save');
    await p.waitForFunction(()=>Object.values(State.notes).some(n=>n.text==='FRESH_REAUDIT_NOTE'));
    const pre=await p.evaluate(()=>({read:[...State.read],activeDay:State.activeDay,activeAppendix:State.activeAppendix,textSize:State.textSize,note:Object.values(State.notes).some(n=>n.text==='FRESH_REAUDIT_NOTE'),theme:localStorage.getItem('mjv_theme')}));
    await p.reload({waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    const persisted=await p.evaluate(()=>({read:[...State.read],activeDay:State.activeDay,activeAppendix:State.activeAppendix,textSize:State.textSize,note:Object.values(State.notes).some(n=>n.text==='FRESH_REAUDIT_NOTE'),theme:localStorage.getItem('mjv_theme')}));
    if(!persisted.read.length||persisted.textSize!=='xlarge'||!persisted.note||persisted.theme!=='dark') throw new Error('mobile persistence '+JSON.stringify(persisted));
    await p.click('#nav-espace'); await p.waitForSelector('#screen-espace.active .cycle-btn');
    await p.click('#screen-espace.active .cycle-btn'); await p.waitForSelector('#cycle-reset-modal.open');
    await p.click('#cycle-reset-confirm');
    await p.waitForFunction(()=>State.read.size===0&&State.activeDay===null&&State.activeAppendix===null);
    const afterCycle=await p.evaluate(()=>({read:State.read.size,activeDay:State.activeDay,activeAppendix:State.activeAppendix,note:Object.values(State.notes).some(n=>n.text==='FRESH_REAUDIT_NOTE'),textSize:State.textSize}));
    if(afterCycle.read!==0||afterCycle.activeDay!==null||afterCycle.activeAppendix!==null||!afterCycle.note||afterCycle.textSize!=='xlarge') throw new Error('cycle reset interaction '+JSON.stringify(afterCycle));
    const bad=badErrors(errors); if(bad.length) throw new Error('mobile runtime errors '+JSON.stringify(bad));
    report.mobile={core,results,unit,pre,persisted,afterCycle,errors};
    await c.close();
  }

  // 3. Android fallback path: paragraph-tap -> contextual bar -> whole-paragraph highlight -> reopen.
  {
    const c=await browser.newContext({
      viewport:{width:412,height:915},colorScheme:'dark',
      userAgent:'Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0 Mobile Safari/537.36'
    });
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
    let p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p); const core=await assertCore(p,'android');
    await p.click('.cal-cell[data-day="1"]'); await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
    const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
    await p.locator('#reader-body p[data-pid]').first().click({position:{x:80,y:20}});
    await p.waitForSelector('#sel-bar.open');
    const label=await p.locator('#sel-bar').getAttribute('aria-label');
    if(label!=='Actions sur le paragraphe') throw new Error('android fallback did not use paragraph mode '+label);
    await p.click('#sel-action-highlight'); await p.waitForSelector('#hl-picker.open');
    await p.locator('#hlp-swatches .hlp-swatch').first().click();
    await p.waitForFunction(pid=>State.highlights.has(pid),pid);
    const before=await p.evaluate(pid=>({records:(State.highlights.get(pid)||[]).length,whole:(State.highlights.get(pid)||[]).some(h=>!h.range)}),pid);
    if(!before.records||!before.whole) throw new Error('android whole highlight absent '+JSON.stringify(before));
    await p.reload({waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    await p.click('.cal-cell[data-day="1"]'); await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
    const after=await p.evaluate(pid=>({records:(State.highlights.get(pid)||[]).length,whole:(State.highlights.get(pid)||[]).some(h=>!h.range)}),pid);
    if(!after.records||!after.whole) throw new Error('android highlight persistence '+JSON.stringify(after));
    const bad=badErrors(errors); if(bad.length) throw new Error('android runtime errors '+JSON.stringify(bad));
    report.android={core,pid,before,after,errors};
    await c.close();
  }

  // 4. Wide/iPad path: search, reader, Help, note placeholder and disclosure controls.
  {
    const c=await browser.newContext({viewport:{width:820,height:1180},colorScheme:'dark'});
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
    const p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p); const core=await assertCore(p,'wide');
    await p.click('#wnav-search'); await p.fill('#wide-search-input','Fiat'); await p.waitForSelector('#wide-list-scroll .snippet-card');
    const results=await p.locator('#wide-list-scroll .snippet-card').count(); if(results<1) throw new Error('wide search no results');
    await p.locator('#wide-list-scroll .snippet-card').first().click(); await p.waitForFunction(()=>document.getElementById('wide-reader-content').style.display!=='none');
    const pid=await p.locator('#wide-reader-body p[data-pid]').first().getAttribute('data-pid');
    await p.evaluate(pid=>App.openNoteModal(pid),pid); await p.waitForSelector('#note-modal.open');
    const ph=await contrastFor(p,'#note-textarea','::placeholder'); if(!ph||ph.ratio<4.5) throw new Error('wide note placeholder contrast '+JSON.stringify(ph));
    await p.click('#note-modal [data-csp-click="App.closeNoteModal()"]');
    await p.click('#wnav-aide'); await p.waitForSelector('#wide-aide .help-nav a');
    const nav=await contrastFor(p,'#wide-aide .help-nav a'); if(!nav||nav.ratio<4.5) throw new Error('wide help nav contrast '+JSON.stringify(nav));
    const sum='#wide-aide details.transfer-card > summary'; await p.waitForSelector(sum); const arrow=await contrastFor(p,sum,'::after'); if(!arrow||arrow.ratio<4.5) throw new Error('wide help arrow contrast '+JSON.stringify(arrow));
    const bad=badErrors(errors); if(bad.length) throw new Error('wide runtime errors '+JSON.stringify(bad));
    report.wide={core,results,pid,notePlaceholder:ph,helpNav:nav,helpArrow:arrow,errors};
    await c.close();
  }

  // 5. Deep-link normal + stale/invalid path.
  {
    const c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'light'});
    await c.addInitScript(()=>localStorage.setItem('mjv_onboarded','1'));
    let p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE+'?open=search&q=Fiat',{waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    const valid=await p.evaluate(()=>({screen:document.getElementById('screen-list').classList.contains('active'),q:document.getElementById('search-input').value,results:document.querySelectorAll('#list-scroll .snippet-card').length,search:location.search}));
    if(!valid.screen||valid.q!=='Fiat'||valid.results<1) throw new Error('valid deep link '+JSON.stringify(valid));
    await p.goto(BASE+'?open=unit&unit=DOES_NOT_EXIST',{waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    const invalid=await p.evaluate(()=>({home:document.getElementById('screen-home').classList.contains('active'),search:location.search,toast:document.getElementById('toast').textContent}));
    if(!invalid.home||invalid.search) throw new Error('invalid deep link did not safely fall back '+JSON.stringify(invalid));
    const bad=badErrors(errors); if(bad.length) throw new Error('deep-link runtime errors '+JSON.stringify(bad));
    report.deepLinks={valid,invalid,errors};
    await c.close();
  }

  // 6. Backup envelope: fresh valid snapshot + deliberate corruption rejection.
  {
    const c=await browser.newContext({viewport:{width:390,height:844}});
    await c.addInitScript(()=>localStorage.setItem('mjv_onboarded','1'));
    const p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p);
    const x=await p.evaluate(()=>{
      const env=App.buildBackupEnvelope(new Date().toISOString());
      const ok=Pure.validateBackupEnvelope(env,App.backupValidationContext());
      const badFormat=JSON.parse(JSON.stringify(env)); badFormat.format='NOT_MJV';
      const bad1=Pure.validateBackupEnvelope(badFormat,App.backupValidationContext());
      const extra=JSON.parse(JSON.stringify(env)); extra.state.unexpected='x';
      const bad2=Pure.validateBackupEnvelope(extra,App.backupValidationContext());
      return {schema:env.schema_version,ok:ok.ok,okErrors:ok.errors||[],badFormat:bad1.ok,badExtra:bad2.ok};
    });
    if(!x.ok||x.schema!==4||x.badFormat||x.badExtra) throw new Error('backup validation '+JSON.stringify(x));
    const bad=badErrors(errors); if(bad.length) throw new Error('backup runtime errors '+JSON.stringify(bad));
    report.backupValidation={...x,errors}; await c.close();
  }

  // 7. Exact v46 -> packaged v48 same-scope update, stale-cache challenge and cold offline reopen.
  {
    fs.rmSync(UPDATE_ROOT,{recursive:true,force:true}); fs.cpSync('marie-v46',UPDATE_ROOT,{recursive:true});
    const c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
    let p=await c.newPage(), errors=[]; await attachErrors(p,errors);
    await p.goto(UPDATE_BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p,'46');
    await p.evaluate(()=>localStorage.setItem('FRESH_REAUDIT_UPDATE_SENTINEL','keep'));
    await p.click('.cal-cell[data-day="1"]'); await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
    await p.click('#btn-complete'); await p.waitForFunction(()=>State.read.size>0);
    await p.evaluate(()=>navigator.serviceWorker.ready);
    fs.rmSync(UPDATE_ROOT,{recursive:true,force:true}); fs.cpSync(ROOT,UPDATE_ROOT,{recursive:true});
    await p.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration(); if(!r) throw new Error('no registration'); await r.update(); await new Promise(res=>setTimeout(res,2500));});
    await p.close(); await new Promise(r=>setTimeout(r,500));
    p=await c.newPage(); await attachErrors(p,errors);
    await p.goto(UPDATE_BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p,'48');
    const post=await p.evaluate(()=>({v:APP_VERSION,read:State.read.size,sentinel:localStorage.getItem('FRESH_REAUDIT_UPDATE_SENTINEL'),loading:document.getElementById('screen-loading').classList.contains('active'),version:document.getElementById('mobile-version').textContent,controller:!!navigator.serviceWorker.controller,caches:null}));
    post.caches=await p.evaluate(()=>caches.keys());
    if(post.v!=='48'||post.read<1||post.sentinel!=='keep'||post.loading||post.version!=='v48'||!post.controller) throw new Error('update state '+JSON.stringify(post));
    const own=post.caches.filter(x=>x.startsWith('mjv-'));
    if(!own.some(x=>/-shell-v48$/.test(x))||!own.some(x=>/-content-v3$/.test(x))||own.some(x=>/-shell-v46$/.test(x))) throw new Error('stale/new cache contradiction '+JSON.stringify(own));
    await c.setOffline(true); await p.close(); p=await c.newPage(); await attachErrors(p,errors);
    await p.goto(UPDATE_BASE+'?open=search&q=Fiat',{waitUntil:'domcontentloaded',timeout:30000}); await ready(p,'48');
    const off=await p.evaluate(()=>({v:APP_VERSION,loading:document.getElementById('screen-loading').classList.contains('active'),version:document.getElementById('mobile-version').textContent,sentinel:localStorage.getItem('FRESH_REAUDIT_UPDATE_SENTINEL'),read:State.read.size,q:document.getElementById('search-input').value,results:document.querySelectorAll('#list-scroll .snippet-card').length}));
    if(off.v!=='48'||off.loading||off.version!=='v48'||off.sentinel!=='keep'||off.read<1||off.q!=='Fiat'||off.results<1) throw new Error('offline post-update '+JSON.stringify(off));
    const bad=badErrors(errors); if(bad.length) throw new Error('update/offline runtime errors '+JSON.stringify(bad));
    report.updateOffline={post,offline:off,errors}; await c.close();
  }

  await browser.close();
  report.status='PASS';
  fs.writeFileSync('MJV_v48_B3_FRESH_REAUDIT_RUNTIME_2026-10-04.json',JSON.stringify(report,null,2));
  console.log('MJV_V48_B3_FRESH_REAUDIT_PASS');
})().catch(e=>{console.error(e);process.exit(2)});