const { chromium } = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('fs');
const crypto = require('crypto');

const CANDIDATE='24h-v120-b4-darkmode';
const PREDECESSOR='24h-v119-b1-governed-r4';
const OUT='blind-24h-v120b4-audit';
fs.mkdirSync(OUT,{recursive:true});
const report={candidate:CANDIDATE,predecessor:PREDECESSOR,generated:new Date().toISOString(),static:{},runs:[],targeted:[],pwa:{},errors:[]};

function sha256(s){return crypto.createHash('sha256').update(s).digest('base64');}
function fileSha256(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');}

function staticAudit(){
  const a=fs.readFileSync(CANDIDATE+'/index.html','utf8');
  const b=fs.readFileSync(CANDIDATE+'/luisa_24_heures.html','utf8');
  const sw=fs.readFileSync(CANDIDATE+'/sw.js','utf8');
  const manifest=JSON.parse(fs.readFileSync(CANDIDATE+'/manifest.json','utf8'));
  const version=JSON.parse(fs.readFileSync(CANDIDATE+'/version.json','utf8'));
  const pm=fs.readFileSync(PREDECESSOR+'/index.html','utf8');
  report.static.index_equals_luisa = fileSha256(CANDIDATE+'/index.html')===fileSha256(CANDIDATE+'/luisa_24_heures.html');
  report.static.app_version=version.app_version;
  report.static.cache_name=version.cache_name;
  report.static.manifest_start_url=manifest.start_url;
  report.static.sw_has_v120b4=/v120-b4/i.test(sw);
  report.static.predecessor_bytes=a.length;
  report.static.changed_index_bytes=a.length-pm.length;
  const styleMatch=a.match(/<style id="dark-mode-contrast-closure-v120">([\s\S]*?)<\/style>/);
  report.static.closure_style_present=!!styleMatch;
  if(styleMatch){
    const actual=sha256(styleMatch[1]);
    const meta=(a.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
    report.static.closure_style_sha256_base64=actual;
    report.static.closure_style_authorized_by_csp=meta.includes("'sha256-"+actual+"'");
  }
  const required=[
    'html[data-theme="dark"] .onboarding-primary',
    'html[data-theme="dark"] .sr-badge.reflection',
    'html[data-theme="dark"] .sr-badge.speech',
    'html[data-theme="dark"] .stage6m-home-action .d',
    'html[data-theme="dark"] .bn-item'
  ];
  report.static.required_closure_selectors=Object.fromEntries(required.map(x=>[x,a.includes(x)]));
}

async function setThemeAndView(page, themeMode, view){
  await page.evaluate(({themeMode,view})=>{
    if(typeof state!=='undefined'){
      state.themePreference=themeMode==='system'?'system':themeMode;
      if(typeof applyTheme==='function') applyTheme();
    } else {
      document.documentElement.setAttribute('data-theme',themeMode==='system'?'dark':themeMode);
    }
    if(document.getElementById('helpModalOverlay') && typeof closeHelpModal==='function') closeHelpModal();
    if(document.getElementById('stage6mSettingsOverlay') && typeof closeSettingsSheet==='function') closeSettingsSheet();
    if(view==='home' && typeof showHome==='function') showHome();
    if(view==='hours' && typeof showHoursView==='function') showHoursView(false);
    if(view==='search' && typeof showSearchView==='function') showSearchView(false);
    if(view==='espace' && typeof showEspaceView==='function') showEspaceView(false);
    if(view==='reader' && typeof openHour==='function') openHour(1,false,{resume:false});
    if(view==='help' && typeof showHelp==='function') { showHome(); showHelp(); }
    if(view==='settings' && typeof showSettingsSheet==='function') { showHome(); showSettingsSheet(); }
    if(view==='prayer' && typeof openPrayer==='function' && typeof CORPUS!=='undefined' && CORPUS.prayers?.length) openPrayer(CORPUS.prayers[0].prayer_id,false);
    if(view==='section' && typeof openSection==='function' && typeof CORPUS!=='undefined' && CORPUS.sections?.length) openSection(CORPUS.sections[0].section_id,false);
  },{themeMode,view});
  await page.waitForTimeout(180);
}

async function scanPage(page,label){
  const result=await page.evaluate(async ({label})=>{
    const visible=el=>{
      const r=el.getBoundingClientRect(),s=getComputedStyle(el);
      return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0;
    };
    const parse=c=>{
      const m=String(c).match(/rgba?\(([^)]+)\)/); if(!m)return null;
      const p=m[1].split(/,\s*/).map(Number); return {r:p[0],g:p[1],b:p[2],a:p[3]===undefined?1:p[3]};
    };
    const comp=(fg,bg)=>({r:Math.round(fg.r*fg.a+bg.r*(1-fg.a)),g:Math.round(fg.g*fg.a+bg.g*(1-fg.a)),b:Math.round(fg.b*fg.a+bg.b*(1-fg.a)),a:1});
    const bgFor=el=>{
      let cur=el,acc={r:255,g:255,b:255,a:1},chain=[];
      while(cur&&cur!==document.documentElement.parentElement){
        const s=getComputedStyle(cur); chain.push(s.backgroundColor);
        if(s.backgroundImage&&s.backgroundImage!=='none') return {skip:'background-image'};
        const c=parse(s.backgroundColor);
        if(c&&c.a>0){ acc=comp(c,acc); if(c.a>=0.999)break; }
        cur=cur.parentElement;
      }
      return {color:acc,chain};
    };
    const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)};
    const ratio=(a,b)=>{const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)};
    const key=el=>el.id?('#'+el.id):(el.tagName.toLowerCase()+([...el.classList].slice(0,3).map(x=>'.'+x).join('')));
    const fails=[];
    for(const el of document.querySelectorAll('body *')){
      if(!visible(el))continue;
      const direct=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
      if(!direct)continue;
      const s=getComputedStyle(el),fg=parse(s.color),bg=bgFor(el);
      if(!fg||bg.skip)continue;
      const cr=ratio(fg,bg.color),size=parseFloat(s.fontSize),weight=parseInt(s.fontWeight)||400;
      const large=size>=24||(size>=18.66&&weight>=700),need=large?3:4.5;
      if(cr+0.01<need)fails.push({type:'text',sel:key(el),text:direct.slice(0,100),ratio:+cr.toFixed(2),need,color:s.color,bg:s.backgroundColor,fontSize:size,weight});
    }
    for(const el of document.querySelectorAll('button, [role="button"], a, input, select, textarea')){
      if(!visible(el))continue;
      const s=getComputedStyle(el),fg=parse(s.color),bg=bgFor(el);
      if(!fg||bg.skip)continue;
      const hasGraphic=!!el.querySelector('svg') || (el.textContent.trim().length<=3 && el.textContent.trim().length>0);
      if(hasGraphic){
        const cr=ratio(fg,bg.color);
        if(cr<2.99)fails.push({type:'control-icon',sel:key(el),text:el.getAttribute('aria-label')||el.textContent.trim().slice(0,50),ratio:+cr.toFixed(2),need:3,color:s.color,bg:s.backgroundColor});
      }
    }
    const overflow={scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,bodyScrollWidth:document.body.scrollWidth};
    return {label,fails,overflow,theme:document.documentElement.getAttribute('data-theme'),view:(typeof state!=='undefined'?state.view:null)};
  },{label});
  try {
    const ar = await new AxeBuilder({page}).withRules(['color-contrast']).analyze();
    result.axe = ar.violations.flatMap(v=>v.nodes.map(n=>({rule:v.id,impact:v.impact,target:n.target,html:(n.html||'').slice(0,180),summary:n.failureSummary||''})));
  } catch(e) {
    result.axeError = String(e);
    result.axe = [];
  }
  return result;
}

async function targeted(page,themeMode){
  await setThemeAndView(page,themeMode,'home');
  const actual=await page.evaluate(()=>{
    const get=sel=>{const e=document.querySelector(sel);if(!e)return null;const s=getComputedStyle(e);return {color:s.color,bg:s.backgroundColor,border:s.borderColor,display:s.display,text:e.textContent.trim().replace(/\s+/g,' ').slice(0,120)}};
    return {
      primary:get('.onboarding-primary'),
      desc:get('.stage6m-home-action .d'),
      navActive:get('.bottom-nav .bn-item.active'),
      navInactive:get('.bottom-nav .bn-item:not(.active)')
    };
  });
  // Search actual badges using multiple broad queries.
  const badgeHits={};
  await page.evaluate(()=>showSearchView(false));
  for(const q of ['Jésus','amour','souffrance','prière','heure']){
    await page.fill('.search-input',q).catch(()=>{});
    await page.evaluate(()=>{const e=document.querySelector('.search-input');if(e&&typeof onSearchInput==='function') onSearchInput(e);});
    await page.waitForTimeout(120);
    const hit=await page.evaluate(()=>{
      const g=sel=>{const e=document.querySelector(sel);if(!e)return null;const s=getComputedStyle(e);return {text:e.textContent.trim(),color:s.color,bg:s.backgroundColor,border:s.borderColor}};
      return {reflection:g('.sr-badge.reflection'),speech:g('.sr-badge.speech')};
    });
    if(hit.reflection&&!badgeHits.reflection) badgeHits.reflection={q,...hit.reflection};
    if(hit.speech&&!badgeHits.speech) badgeHits.speech={q,...hit.speech};
    if(badgeHits.reflection&&badgeHits.speech)break;
  }
  // Bottom nav semantics through all four real routes.
  const nav=[];
  for(const id of ['bnHome','bnHours','bnSearch','bnEspace']){
    await page.click('#'+id);
    await page.waitForTimeout(80);
    nav.push(await page.evaluate(id=>({
      clicked:id,
      active:[...document.querySelectorAll('.bn-item.active')].map(e=>e.id),
      current:[...document.querySelectorAll('.bn-item[aria-current="page"]')].map(e=>e.id),
      stateView:typeof state!=='undefined'?state.view:null
    }),id));
  }
  return {themeMode,actual,badgeHits,nav};
}

async function focusAudit(page){
  await setThemeAndView(page,'dark','home');
  const out=[];
  for(let i=0;i<18;i++){
    await page.keyboard.press('Tab');
    const v=await page.evaluate(()=>{
      const e=document.activeElement;if(!e||e===document.body)return null;const s=getComputedStyle(e);const r=e.getBoundingClientRect();
      return {tag:e.tagName,id:e.id,cls:e.className,label:e.getAttribute('aria-label')||e.textContent.trim().replace(/\s+/g,' ').slice(0,70),outline:s.outline,outlineColor:s.outlineColor,outlineWidth:s.outlineWidth,rect:{x:r.x,y:r.y,w:r.width,h:r.height}};
    });
    if(v)out.push(v);
  }
  return out;
}

async function runPath(browser,path,label){
  for(const viewport of [{name:'iphone',w:390,h:844},{name:'ipad',w:820,h:1180}]){
    for(const mode of ['dark','system']){
      const ctx=await browser.newContext({viewport:{width:viewport.w,height:viewport.h},colorScheme:'dark'});
      await ctx.addInitScript(()=>{localStorage.setItem('lp24_onboarded','1');localStorage.setItem('blind_sentinel','preserve-me');});
      const page=await ctx.newPage();
      const consoleErrors=[]; const pageErrors=[];
      page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
      page.on('pageerror',e=>pageErrors.push(String(e)));
      const res=await page.goto('http://127.0.0.1:8080/'+path+'/luisa_24_heures.html',{waitUntil:'domcontentloaded',timeout:120000});
      await page.waitForFunction(()=>typeof showHome==='function',{timeout:30000});
      await page.waitForTimeout(600);
      for(const view of ['home','hours','search','espace','reader','help','settings','prayer','section']){
        await setThemeAndView(page,mode,view);
        const scan=await scanPage(page,label+'-'+viewport.name+'-'+mode+'-'+view);
        scan.consoleErrors=[...consoleErrors]; scan.pageErrors=[...pageErrors];
        report.runs.push(scan);
        if(label==='after') await page.screenshot({path:OUT+'/'+viewport.name+'_'+mode+'_'+view+'.png',fullPage:false});
      }
      if(label==='after'){
        report.targeted.push({viewport:viewport.name,...await targeted(page,mode)});
        report.focus=report.focus||{};
        if(viewport.name==='iphone'&&mode==='dark') report.focus.iphone_dark=await focusAudit(page);
      }
      const sentinel=await page.evaluate(()=>localStorage.getItem('blind_sentinel'));
      if(sentinel!=='preserve-me') report.errors.push(label+' '+viewport.name+' '+mode+' lost sentinel');
      await ctx.close();
    }
  }
}

async function pwaAudit(browser){
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  const page=await ctx.newPage();
  await page.goto('http://127.0.0.1:8080/'+CANDIDATE+'/luisa_24_heures.html',{waitUntil:'networkidle',timeout:120000});
  await page.evaluate(()=>localStorage.setItem('blind_pwa_sentinel','keep'));
  const reg=await page.evaluate(async()=>{if(!('serviceWorker'in navigator))return {supported:false}; const r=await navigator.serviceWorker.ready; return {supported:true,scope:r.scope,active:r.active?.state};});
  await page.reload({waitUntil:'networkidle',timeout:120000});
  await ctx.setOffline(true);
  let offlineOk=false,offlineText='';
  try{
    await page.reload({waitUntil:'domcontentloaded',timeout:30000});
    offlineText=(await page.locator('body').innerText()).slice(0,300);
    offlineOk=offlineText.includes('24 Heures');
  }catch(e){offlineText=String(e);}
  const sentinel=await page.evaluate(()=>localStorage.getItem('blind_pwa_sentinel')).catch(()=>null);
  report.pwa={registration:reg,offlineOk,sentinel,offlineText};
  await ctx.close();
}

(async()=>{
  staticAudit();
  const browser=await chromium.launch({headless:true});
  await runPath(browser,PREDECESSOR,'before');
  await runPath(browser,CANDIDATE,'after');
  await pwaAudit(browser);
  await browser.close();

  const sig=x=>x.type+'|'+x.sel+'|'+x.text;
  const beforeFails=new Set(report.runs.filter(r=>r.label.startsWith('before-')).flatMap(r=>r.fails.map(sig)));
  const afterFails=report.runs.filter(r=>r.label.startsWith('after-')).flatMap(r=>r.fails);
  report.delta={
    newCustomFailures:[...new Map(afterFails.filter(x=>!beforeFails.has(sig(x))).map(x=>[sig(x),x])).values()],
    afterCustomFailureCount:afterFails.length,
    beforeCustomFailureCount:report.runs.filter(r=>r.label.startsWith('before-')).reduce((n,r)=>n+r.fails.length,0),
    afterAxeCount:report.runs.filter(r=>r.label.startsWith('after-')).reduce((n,r)=>n+r.axe.length,0),
    beforeAxeCount:report.runs.filter(r=>r.label.startsWith('before-')).reduce((n,r)=>n+r.axe.length,0),
    overflowAfter:report.runs.filter(r=>r.label.startsWith('after-')).filter(r=>r.overflow.scrollWidth>r.overflow.clientWidth+1).map(r=>({label:r.label,...r.overflow})),
    consoleErrorsAfter:[...new Set(report.runs.filter(r=>r.label.startsWith('after-')).flatMap(r=>r.consoleErrors||[]))],
    pageErrorsAfter:[...new Set(report.runs.filter(r=>r.label.startsWith('after-')).flatMap(r=>r.pageErrors||[]))]
  };
  fs.writeFileSync(OUT+'/REPORT.json',JSON.stringify(report,null,2));
  const summary={
    static:report.static,
    delta:report.delta,
    pwa:report.pwa,
    targeted:report.targeted,
    focusCount:report.focus?.iphone_dark?.length||0
  };
  fs.writeFileSync(OUT+'/SUMMARY.json',JSON.stringify(summary,null,2));
  console.log(JSON.stringify(summary,null,2));
  const hard=[];
  if(!report.static.index_equals_luisa)hard.push('index/luisa mismatch');
  if(report.static.app_version!=='v120')hard.push('wrong version');
  if(!report.static.closure_style_authorized_by_csp)hard.push('closure CSP not authorized');
  if(report.delta.newCustomFailures.length)hard.push('new custom contrast failures '+report.delta.newCustomFailures.length);
  if(report.delta.overflowAfter.length)hard.push('horizontal overflow');
  if(report.delta.pageErrorsAfter.length)hard.push('page errors');
  if(!report.pwa.offlineOk||report.pwa.sentinel!=='keep')hard.push('PWA/offline/state failure');
  for(const t of report.targeted){
    if(t.nav.some(n=>n.active.length!==1||n.current.length!==1)) hard.push('bottom nav semantic failure '+t.viewport+' '+t.themeMode);
  }
  if(hard.length){console.error('BLIND_ADVERSARIAL_FAIL',hard);process.exit(2);}
  console.log('BLIND_ADVERSARIAL_PASS');
})().catch(e=>{console.error(e);process.exit(1)});