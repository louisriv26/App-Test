const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');

const PACK='_blind_marie_v48_b3';
const BASE='http://127.0.0.1:8082/'+PACK+'/';
const UPG='_blind_marie_v48_b3_upgrade';
const UBASE='http://127.0.0.1:8082/'+UPG+'/';

function rgb(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}}
function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
function L(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}
function ratio(a,b){return (Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
async function waitReady(p,v='48'){
  await p.waitForFunction(v=>{
    const load=document.getElementById('screen-loading');
    const mv=document.getElementById('mobile-version');
    return typeof APP_VERSION!=='undefined' && APP_VERSION===v &&
      typeof State!=='undefined' && Array.isArray(State.corpus) && State.corpus.length===37 &&
      load && !load.classList.contains('active') && mv && mv.textContent==='v'+v;
  },v,{timeout:30000});
}
async function placeholderRatio(p,sel){
  return p.$eval(sel,el=>{
    function rgb(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2]}}
    function ln(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
    function L(c){return .2126*ln(c.r)+.7152*ln(c.g)+.0722*ln(c.b)}
    function R(a,b){return(Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
    const fg=rgb(getComputedStyle(el,'::placeholder').color),bg=rgb(getComputedStyle(el).backgroundColor);
    return {ratio:R(fg,bg),fg:getComputedStyle(el,'::placeholder').color,bg:getComputedStyle(el).backgroundColor};
  });
}
async function normalContrast(p,sel){
  return p.$eval(sel,el=>{
    function rgb(s){const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2]}}
    function ln(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
    function L(c){return .2126*ln(c.r)+.7152*ln(c.g)+.0722*ln(c.b)}
    function R(a,b){return(Math.max(L(a),L(b))+.05)/(Math.min(L(a),L(b))+.05)}
    const cs=getComputedStyle(el),fg=rgb(cs.color),bg=rgb(cs.backgroundColor);return{ratio:R(fg,bg),fg:cs.color,bg:cs.backgroundColor};
  });
}
function resetDir(dst,src){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true});}

(async()=>{
  const browser=await chromium.launch({headless:true});
  const matrix=[];
  const configs=[
    {name:'phone-alt',w:375,h:812},
    {name:'tablet-portrait-alt',w:768,h:1024},
    {name:'tablet-landscape-alt',w:1024,h:768},
  ];
  for(const cfg of configs){
    for(const mode of ['light','dark','system']){
      const ctx=await browser.newContext({viewport:{width:cfg.w,height:cfg.h},colorScheme:mode==='light'?'light':'dark'});
      await ctx.addInitScript(mode=>{localStorage.setItem('mjv_onboarded','1');if(mode==='system')localStorage.removeItem('mjv_theme');else localStorage.setItem('mjv_theme',mode)},mode);
      const p=await ctx.newPage(),errs=[];
      p.on('pageerror',e=>errs.push('PAGE '+String(e)));
      p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});
      const resp=await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});await waitReady(p);
      const core=await p.evaluate(()=>({
        version:APP_VERSION,corpus:State.corpus.length,self:App.selfTest(),
        mobile:document.getElementById('mobile-version').textContent,
        desktop:document.getElementById('desktop-version').textContent,
        loading:document.getElementById('screen-loading').classList.contains('active'),
        scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,
        wide:typeof isWide==='function'?isWide():window.innerWidth>=768
      }));
      if(core.self.total!==156||core.self.passed!==156||core.self.failed.length||core.loading||core.mobile!=='v48'||core.desktop!=='v48'||core.scrollWidth>core.clientWidth+1)
        throw new Error(cfg.name+' '+mode+' core '+JSON.stringify(core));
      const wide=core.wide;
      if(wide){await p.click('#wnav-search');await p.fill('#wide-search-input','Divine Volonté');await p.waitForSelector('#wide-list-scroll .snippet-card');}
      else{await p.click('#nav-search');await p.fill('#search-input','Divine Volonté');await p.waitForSelector('#list-scroll .snippet-card');}
      const searchSel=wide?'#wide-search-input':'#search-input';
      const sr=await placeholderRatio(p,searchSel);if(sr.ratio<4.5)throw new Error(cfg.name+' '+mode+' search placeholder '+JSON.stringify(sr));
      const card=p.locator(wide?'#wide-list-scroll .snippet-card':'#list-scroll .snippet-card').first();await card.click();
      const bodySel=wide?'#wide-reader-body':'#reader-body';
      await p.waitForFunction(w=>w?document.getElementById('wide-reader-body').innerText.length>100:document.getElementById('screen-reader').classList.contains('active'),wide);
      const pid=await p.locator(bodySel+' p[data-pid]').first().getAttribute('data-pid');if(!pid)throw new Error('blind missing pid');
      await p.evaluate(pid=>App.openNoteModal(pid),pid);await p.waitForSelector('#note-modal.open');
      const nr=await placeholderRatio(p,'#note-textarea');if(nr.ratio<4.5)throw new Error(cfg.name+' '+mode+' note placeholder '+JSON.stringify(nr));
      await p.click('#note-modal [data-csp-click="App.closeNoteModal()"]');
      if(wide){await p.click('#wnav-espace');await p.waitForSelector('#wide-espace .backup-btn.primary');}
      else{await p.evaluate(()=>App.showScreen('espace'));await p.waitForSelector('#screen-espace.active .backup-btn.primary');}
      if(mode!=='light'){
        const sel=wide?'#wide-espace .backup-btn.primary':'#screen-espace .backup-btn.primary';
        const btn=p.locator(sel).first();await btn.hover();const hr=await normalContrast(p,sel);await btn.focus();const fr=await normalContrast(p,sel);
        if(hr.ratio<4.5||fr.ratio<4.5)throw new Error(cfg.name+' '+mode+' primary action '+JSON.stringify({hr,fr}));
      }
      if(wide){await p.click('#wnav-aide');if((await p.locator('#wide-aide').innerText()).length<300)throw new Error('blind wide help empty');}
      else{await p.evaluate(()=>App.openHelp());if((await p.locator('#screen-aide').innerText()).length<300)throw new Error('blind mobile help empty');}
      const bad=errs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));if(bad.length)throw new Error(cfg.name+' '+mode+' errors '+JSON.stringify(bad));
      matrix.push({viewport:cfg.name,mode,http:resp.status(),core,search_placeholder:sr,note_placeholder:nr,errors:errs});
      await ctx.close();
    }
  }

  // Independent package-based production-predecessor migration.
  resetDir(UPG,'marie-v46');
  const ctx=await browser.newContext({viewport:{width:393,height:852},colorScheme:'dark'});
  await ctx.addInitScript(()=>localStorage.setItem('mjv_onboarded','1'));
  let p=await ctx.newPage(),errs=[];const wire=x=>{x.on('pageerror',e=>errs.push('PAGE '+String(e)));x.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())})};wire(p);
  await p.goto(UBASE,{waitUntil:'domcontentloaded',timeout:120000});await waitReady(p,'46');
  await p.evaluate(()=>{localStorage.setItem('BLIND_MARIE_SENTINEL','KEEP');localStorage.setItem('mjv_theme','dark')});
  await p.waitForFunction(()=>!!navigator.serviceWorker.controller,{timeout:20000}).catch(()=>{});
  resetDir(UPG,PACK);
  await p.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();if(!r)throw new Error('blind no predecessor SW');await r.update();await new Promise(r=>setTimeout(r,1800))});
  await p.close();await new Promise(r=>setTimeout(r,500));p=await ctx.newPage();wire(p);
  await p.goto(UBASE,{waitUntil:'domcontentloaded',timeout:120000});await waitReady(p,'48');
  const up=await p.evaluate(()=>({v:APP_VERSION,sentinel:localStorage.getItem('BLIND_MARIE_SENTINEL'),theme:localStorage.getItem('mjv_theme'),versionText:document.getElementById('mobile-version').textContent,caches:null}));
  up.caches=await p.evaluate(()=>caches.keys());
  if(up.sentinel!=='KEEP'||up.theme!=='dark'||up.versionText!=='v48'||!up.caches.some(x=>/-shell-v48$/.test(x)))throw new Error('blind upgrade '+JSON.stringify(up));
  await ctx.setOffline(true);await p.close();p=await ctx.newPage();wire(p);await p.goto(UBASE,{waitUntil:'domcontentloaded',timeout:30000});await waitReady(p,'48');
  const off=await p.evaluate(()=>({v:APP_VERSION,sentinel:localStorage.getItem('BLIND_MARIE_SENTINEL'),loading:document.getElementById('screen-loading').classList.contains('active'),versionText:document.getElementById('mobile-version').textContent}));
  if(off.sentinel!=='KEEP'||off.loading||off.versionText!=='v48')throw new Error('blind offline '+JSON.stringify(off));
  const bad=errs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));if(bad.length)throw new Error('blind update errors '+JSON.stringify(bad));
  await ctx.close();await browser.close();

  const out={candidate:'MJV v48/B3',basis:'unpacked deterministic release ZIP',matrix,upgrade:up,offline:off,status:'PASS'};
  fs.writeFileSync('MJV_v48_B3_FINAL_INDEPENDENT_BLIND_EVIDENCE.json',JSON.stringify(out,null,2));
  console.log('MARIE_V48_B3_FINAL_INDEPENDENT_BLIND_PASS',matrix.length);
})().catch(e=>{console.error(e);process.exit(2)});