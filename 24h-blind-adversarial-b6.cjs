
const { chromium } = require('playwright');
const fs = require('fs');

const APP = '24h-v120-b6-blind-closure';
const BASE = 'http://127.0.0.1:8084/' + APP + '/';
const viewports = [
  {name:'iphone-se', width:320, height:568},
  {name:'iphone', width:375, height:812},
  {name:'iphone-large', width:430, height:932},
  {name:'ipad-portrait', width:768, height:1024},
  {name:'ipad-landscape', width:1024, height:768},
  {name:'desktop', width:1366, height:900}
];
const themes = ['light','dark'];
const fonts = ['normal','xlarge'];
const findings = [];
const evidence = {candidate:APP, base:BASE, generated_at:new Date().toISOString(), cases:[], sw:{}, journeys:{}};

function add(sev, code, message, detail={}) { findings.push({severity:sev, code, message, ...detail}); }

async function scanScene(page, meta) {
  const r = await page.evaluate(() => {
    const parse = s => {
      const m=String(s||'').match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\s*\)/i);
      return m ? {r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]} : null;
    };
    const over=(f,b)=>{ if(!f)return b; const a=f.a+b.a*(1-f.a); if(a<=0)return b; return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}; };
    const lum=c=>{const q=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*q(c.r)+.7152*q(c.g)+.0722*q(c.b)};
    const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
    const visible=el=>{const cs=getComputedStyle(el),b=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&+cs.opacity>0&&b.width>0&&b.height>0};
    const bgOf=el=>{let chain=[],n=el;while(n&&n.nodeType===1){chain.unshift(n);n=n.parentElement}let bg={r:255,g:255,b:255,a:1};for(const x of chain){const q=parse(getComputedStyle(x).backgroundColor);if(q&&q.a>0)bg=over(q,bg)}return bg};
    const id=el=>{let s=el.tagName.toLowerCase();if(el.id)s+='#'+el.id;if(el.classList&&el.classList.length)s+='.'+[...el.classList].slice(0,3).join('.');return s};
    const directText=el=>[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ').trim().replace(/\s+/g,' ');
    const textFails=[], iconFails=[], unnamed=[], smallTargets=[];
    const elems=[...document.querySelectorAll('body *')].filter(el=>visible(el) && !el.closest('[aria-hidden="true"]'));
    for(const el of elems){
      if(el.matches(':disabled,[aria-disabled="true"]')) continue;
      const txt=directText(el);
      if(txt){
        const cs=getComputedStyle(el), fg=parse(cs.color), bg=bgOf(el);
        if(fg){
          const effective=over(fg,bg), rr=ratio(effective,bg);
          const symbol=/^[^\p{L}\p{N}]{1,3}$/u.test(txt) && (el.getAttribute('aria-label')||el.getAttribute('title'));
          const fs=parseFloat(cs.fontSize)||16, fw=parseInt(cs.fontWeight)||400;
          const large=fs>=24||(fs>=18.66&&fw>=700), th=symbol?3:(large?3:4.5);
          if(rr+1e-6<th) textFails.push({el:id(el),text:txt.slice(0,80),ratio:+rr.toFixed(2),threshold:th,color:cs.color,background:getComputedStyle(el).backgroundColor});
        }
      }
    }
    const interactive=[...document.querySelectorAll('button,a[href],input,select,textarea,[role="button"],[role="tab"]')].filter(visible);
    for(const el of interactive){
      const name=(el.getAttribute('aria-label')||el.getAttribute('title')||el.textContent||el.getAttribute('placeholder')||'').trim();
      if(!name) unnamed.push({el:id(el)});
      const b=el.getBoundingClientRect();
      if((b.width<44||b.height<44) && !el.matches('a[href]') && !el.closest('.prose,.reader-text,.meditation-content')) smallTargets.push({el:id(el),w:+b.width.toFixed(1),h:+b.height.toFixed(1),name:name.slice(0,80)});
    }
    for(const el of elems.filter(x=>x.matches('svg,[aria-hidden="true"].icon,.icon-btn svg'))){
      const cs=getComputedStyle(el), fg=parse(cs.color), bg=bgOf(el);
      if(fg){const rr=ratio(over(fg,bg),bg); if(rr<3) iconFails.push({el:id(el),ratio:+rr.toFixed(2),color:cs.color});}
    }
    const overflow={docScrollWidth:document.documentElement.scrollWidth,innerWidth:innerWidth,bodyScrollWidth:document.body.scrollWidth};
    const nav=[...document.querySelectorAll('.bottom-nav .bn-item')].filter(visible).map(el=>({id:el.id,text:el.textContent.trim(),rect:el.getBoundingClientRect().toJSON()}));
    return {textFails,iconFails,unnamed,smallTargets,overflow,nav,theme:document.documentElement.getAttribute('data-theme'),font:document.documentElement.getAttribute('data-font-level')};
  });
  evidence.cases.push({...meta,...r});
  if(r.overflow.docScrollWidth>meta.width+2 || r.overflow.bodyScrollWidth>meta.width+2) add('error','LAYOUT-H-OVERFLOW','Horizontal document overflow', {case:meta, overflow:r.overflow});
  for(const f of r.textFails) add('error','A11Y-CONTRAST-TEXT','Visible text/symbol contrast below threshold',{case:meta, finding:f});
  for(const f of r.iconFails) add('error','A11Y-CONTRAST-ICON','Visible icon contrast below 3:1',{case:meta, finding:f});
  for(const f of r.unnamed) add('error','A11Y-NAME','Visible interactive control lacks accessible name',{case:meta, finding:f});
  // Treat touch-target findings as warnings first; adjudicate after evidence review.
  for(const f of r.smallTargets) add('warning','TOUCH-TARGET','Visible non-link control below 44x44 CSS px',{case:meta, finding:f});
  return r;
}

(async()=>{
  const browser=await chromium.launch({headless:true});

  // Cold service-worker install test in a completely clean context.
  {
    const ctx=await browser.newContext({viewport:{width:390,height:844}, colorScheme:'dark'});
    const p=await ctx.newPage();
    const consoleErrors=[], pageErrors=[];
    p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
    p.on('pageerror',e=>pageErrors.push(String(e.message||e)));
    const res=await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});
    await p.waitForFunction(()=>typeof showHome==='function' && !!document.getElementById('content'),null,{timeout:30000});
    await p.waitForTimeout(3500);
    const sw=await p.evaluate(async()=>{
      const reg=await navigator.serviceWorker.getRegistration();
      const snap=()=>reg?{installing:reg.installing&&reg.installing.state,waiting:reg.waiting&&reg.waiting.state,active:reg.active&&reg.active.state,controller:!!navigator.serviceWorker.controller,script:(reg.active||reg.waiting||reg.installing)?.scriptURL||null}:null;
      const first=snap();
      await new Promise(r=>setTimeout(r,3000));
      const second=snap();
      let ready=false; try{await Promise.race([navigator.serviceWorker.ready,new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout')),3000))]);ready=true}catch(_){}
      return {first,second,ready,caches:await caches.keys()};
    });
    evidence.sw={http:res&&res.status(), consoleErrors, pageErrors, ...sw};
    const appCaches=(sw.caches||[]).filter(x=>/-v120-b6$/.test(x));
    const badLiteral=(sw.caches||[]).filter(x=>x.includes('${CACHE_PREFIX}')||x.includes('\\${CACHE_PREFIX}'));
    if(appCaches.length!==1 || !/^luisa-24h-[0-9a-f]{8}-v120-b6$/.test(appCaches[0])) add('error','PWA-CACHE-SCOPE','B6 app cache is not exactly one scope-derived cache',{caches:sw.caches,appCaches});
    if(badLiteral.length) add('error','PWA-CACHE-LITERAL','Literal CACHE_PREFIX interpolation leaked into runtime cache',{badLiteral});
    if(!sw.ready || !sw.second || !sw.second.active) add('error','PWA-COLD-INSTALL','Fresh candidate does not reach an active ready service worker',{sw:evidence.sw});
    if(consoleErrors.some(x=>/service|manifest|CSP|Content Security|Failed to register/i.test(x))) add('error','BROWSER-CONSOLE','Cold load emits service-worker/CSP/manifest console error',{errors:consoleErrors});
    if(pageErrors.length) add('error','PAGE-ERROR','Cold load emitted page error',{errors:pageErrors});
    await ctx.close();
  }

  // Responsive/theme/font matrix and independent scene traversal.
  for(const vp of viewports){
    for(const theme of themes){
      for(const font of fonts){
        const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height},colorScheme:theme});
        const p=await ctx.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(String(e.message||e)));
        await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});
        await p.waitForFunction(()=>typeof showHome==='function' && !!document.getElementById('content'),null,{timeout:30000});
        await p.evaluate(({theme,font})=>{document.documentElement.setAttribute('data-theme',theme);document.documentElement.setAttribute('data-font-level',font);},{theme,font});
        const scenes=[
          ['home',"showHome()"],
          ['hours',"showHoursView()"],
          ['reader1',"openHour(1)"],
          ['search',"showSearchView()"],
          ['espace',"showEspaceView()"],
          ['help',"showHelp()"],
          ['settings',"showSettingsSheet()"]
        ];
        for(const [scene,code] of scenes){
          try{await p.evaluate(code=>{try{(0,eval)(code)}catch(e){throw e}},code);await p.waitForTimeout(120);}catch(e){add('error','SCENE-OPEN','Scene failed to open',{case:{vp:vp.name,theme,font,scene},error:String(e)})}
          await scanScene(p,{vp:vp.name,width:vp.width,height:vp.height,theme,font,scene});
          if(scene==='help') await p.evaluate(()=>typeof closeHelpModal==='function'&&closeHelpModal());
          if(scene==='settings') await p.evaluate(()=>typeof closeSettingsSheet==='function'&&closeSettingsSheet());
        }
        if(errors.length) add('error','PAGE-ERROR-MATRIX','Page errors during matrix traversal',{case:{vp:vp.name,theme,font},errors});
        await ctx.close();
      }
    }
  }

  // Functional journeys: search, tabs, theme, font sizing, focus.
  {
    const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'light'});
    const p=await ctx.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(String(e.message||e)));
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});
    await p.waitForFunction(()=>typeof openHour==='function',null,{timeout:30000});
    const j={};
    j.identity=await p.evaluate(()=>({APP_VERSION,BUILD_REVISION,APP_RELEASE_SEQUENCE,APP_RELEASE_ID,evidenceStage:APP_EVIDENCE_STAGE}));
    await p.evaluate(()=>openHour(1));
    await p.waitForTimeout(150);
    j.tabs=await p.evaluate(()=>[...document.querySelectorAll('[role="tab"]')].map(t=>({id:t.id,name:t.textContent.trim(),controls:t.getAttribute('aria-controls'),selected:t.getAttribute('aria-selected'),panel:t.getAttribute('aria-controls')?document.getElementById(t.getAttribute('aria-controls'))?.getAttribute('role'):null,labelled:t.getAttribute('aria-controls')?document.getElementById(t.getAttribute('aria-controls'))?.getAttribute('aria-labelledby'):null})));
    if(!j.tabs.length || j.tabs.some(x=>!x.controls||x.panel!=='tabpanel'||x.labelled!==x.id)) add('error','ARIA-TABS','Reader tab/tabpanel relationships incomplete',{tabs:j.tabs});
    await p.evaluate(()=>showSearchView());
    await p.waitForTimeout(100);
    const search=await p.locator('input.search-input:visible').first();
    if(await search.count()){
      await search.fill('Jésus'); await search.dispatchEvent('input'); await p.waitForTimeout(250);
      j.search=await p.evaluate(()=>({text:(document.getElementById('content')?.innerText||'').slice(0,3000),results:document.querySelectorAll('.search-result,.search-result-card,.result-card').length}));
      if(!/Jésus/i.test(j.search.text) || /0 résultat/i.test(j.search.text)) add('error','SEARCH-SMOKE','Representative search did not produce visible matching output',{search:j.search});
    } else add('error','SEARCH-INPUT','Search scene has no visible search input');
    await p.evaluate(async()=>{await setThemePreference('dark')}); await p.waitForTimeout(100);
    j.dark=await p.evaluate(()=>document.documentElement.getAttribute('data-theme'));
    if(j.dark!=='dark') add('error','THEME-SWITCH','Explicit dark theme did not apply',{value:j.dark});
    await p.evaluate(()=>changeFontSize('xlarge')); await p.waitForTimeout(100);
    j.font=await p.evaluate(()=>({level:document.documentElement.getAttribute('data-font-level'),reading:getComputedStyle(document.documentElement).getPropertyValue('--reading-size').trim()}));
    if(j.font.level!=='xlarge') add('error','FONT-SWITCH','Très grand font level did not apply',{font:j.font});
    await p.evaluate(()=>showHome()); await p.waitForTimeout(80);
    const focusSelectors=['#stage6mSettingsBtn','#bnHome','#bnHours','#bnSearch','#bnEspace'];
    j.focus=[];
    for(const sel of focusSelectors){
      const loc=p.locator(sel);
      if(await loc.count()){
        await loc.focus();
        const f=await loc.evaluate(el=>{const s=getComputedStyle(el);return{sel:el.id?('#'+el.id):el.tagName,outline:s.outline,outlineWidth:s.outlineWidth,boxShadow:s.boxShadow,borderColor:s.borderColor}});
        j.focus.push(f);
        const noOutline=!f.outline||f.outline==='none'||f.outlineWidth==='0px';
        if(noOutline && (!f.boxShadow||f.boxShadow==='none')) add('error','FOCUS-VISIBLE','Critical control lacks visible focus indicator',{finding:f});
      }
    }
    j.errors=errors; if(errors.length)add('error','PAGE-ERROR-JOURNEY','Functional journey emitted page errors',{errors});
    evidence.journeys=j;
    await ctx.close();
  }

  // Forced-colors representative critical controls.
  {
    const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark',forcedColors:'active'});
    const p=await ctx.newPage(); await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000}); await p.waitForFunction(()=>typeof showHome==='function');
    await p.evaluate(()=>showHome());
    const forced=await p.evaluate(()=>['stage6mSettingsBtn','bnHome','bnHours','bnSearch','bnEspace'].map(id=>{const el=document.getElementById(id),s=el&&getComputedStyle(el);return el?{id,border:s.border,outline:s.outline,color:s.color}:null}).filter(Boolean));
    evidence.forcedColors=forced;
    for(const x of forced){if((!x.border||x.border.startsWith('0px'))&&(!x.outline||x.outline==='none'))add('error','FORCED-COLORS-BOUNDARY','Critical control lacks boundary/outline in forced colors',{finding:x});}
    await ctx.close();
  }

  await browser.close();
  evidence.findings=findings;
  fs.writeFileSync('24h-blind-adversarial-b6-results.json',JSON.stringify(evidence,null,2));
  console.log('BLIND_AUDIT_FINDINGS',findings.length);
  for(const f of findings) console.log(JSON.stringify(f));
})().catch(e=>{console.error(e); try{fs.writeFileSync('24h-blind-adversarial-b6-fatal.txt',String(e&&e.stack||e))}catch(_){} process.exit(1)});
