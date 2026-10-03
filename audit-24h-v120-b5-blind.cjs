const { chromium } = require('playwright');
const fs = require('fs');
const crypto = require('crypto');

const C='24h-v120-b5-blind-adversarial-closure';
const B4='24h-v120-b4-darkmode';
const V119='24h-v119-b1-governed-r4';
const OUT='24h-v120-b5-blind-evidence';
const EXPECT={version:'v120',revision:'B5',sequence:120000002,releaseId:'24h-v120-b5-20261003-blind-adversarial-integrity-closure',shellSha:'88fa5244a953fd022351c330e4ccca740656ec06eef680a8ad1284036a7ccd6b',scriptHash:'sha256-UnF2h8aYOhvEnVR7VK5coakqu8Vjp00a/Bfovzz4loI='};
fs.mkdirSync(OUT,{recursive:true});
const report={expected:EXPECT,static:{},protected:{},browser:[],targets:[],focus:{},forcedColors:{},cleanPwa:{},updatePwa:{},hardFailures:[],warnings:[]};

const shaHex=b=>crypto.createHash('sha256').update(b).digest('hex');
const shaB64=b=>crypto.createHash('sha256').update(b).digest('base64');
const read=p=>fs.readFileSync(p,'utf8');
function constVal(src,name){const m=src.match(new RegExp("const\\s+"+name+"\\s*=\\s*['\\\"]([^'\\\"]+)['\\\"]"));return m?m[1]:null}
function staticAudit(){
  const html=read(C+'/index.html'),luisa=read(C+'/luisa_24_heures.html'),sw=read(C+'/sw.js');
  const manifest=JSON.parse(read(C+'/manifest.json')),version=JSON.parse(read(C+'/version.json'));
  const csp=(html.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
  const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
  const styles=[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(m=>m[1]);
  const scriptHashes=scripts.map(s=>'sha256-'+shaB64(s)),styleHashes=styles.map(s=>'sha256-'+shaB64(s));
  const shellSha=shaHex(fs.readFileSync(C+'/index.html'));
  report.static={
    shellSha,indexLuisaEqual:shaHex(Buffer.from(html))===shaHex(Buffer.from(luisa)),
    scriptHashes,scriptAuthorized:scriptHashes.map(h=>csp.includes("'"+h+"'")),
    styleHashes,styleAuthorized:styleHashes.map(h=>csp.includes("'"+h+"'")),
    shell:{version:constVal(html,'APP_VERSION'),revision:constVal(html,'BUILD_REVISION'),sequence:Number((html.match(/const APP_RELEASE_SEQUENCE = (\d+);/)||[])[1]),releaseId:constVal(html,'APP_RELEASE_ID')},
    sw:{version:constVal(sw,'APP_VERSION'),revision:constVal(sw,'BUILD_REVISION'),sequence:Number((sw.match(/const RELEASE_SEQUENCE = (\d+);/)||[])[1]),releaseId:constVal(sw,'RELEASE_ID'),shellSha:constVal(sw,'CANONICAL_SHELL_SHA256')},
    manifest:{version:manifest.version,revision:manifest.build_revision,sequence:Number(manifest.release_sequence),releaseId:manifest.release_id,startUrl:manifest.start_url},
    version:{version:version.app_version,revision:version.build_revision,sequence:Number(version.release_sequence),releaseId:version.release_id,shellSha:version.canonical_shell_sha256,realDevice:version.real_device_status,overall:version.overall_release_status,scriptHash:version.canonical_shell_inline_script_sha256_csp}
  };
  for(const [k,o] of Object.entries({shell:report.static.shell,sw:report.static.sw,manifest:report.static.manifest,version:report.static.version})){
    if(o.version!==EXPECT.version||o.revision!==EXPECT.revision||o.sequence!==EXPECT.sequence||o.releaseId!==EXPECT.releaseId)report.hardFailures.push('release identity mismatch '+k+': '+JSON.stringify(o));
  }
  if(shellSha!==EXPECT.shellSha)report.hardFailures.push('shell SHA mismatch '+shellSha);
  if(report.static.sw.shellSha!==shellSha||report.static.version.shellSha!==shellSha)report.hardFailures.push('shell hash binding mismatch');
  if(!report.static.indexLuisaEqual)report.hardFailures.push('index/canonical shell mismatch');
  if(scriptHashes.length!==1||scriptHashes[0]!==EXPECT.scriptHash||!report.static.scriptAuthorized.every(Boolean))report.hardFailures.push('inline script CSP binding failure');
  if(!report.static.styleAuthorized.every(Boolean))report.hardFailures.push('inline style CSP binding failure');
  if(manifest.start_url!=='./luisa_24_heures.html')report.hardFailures.push('manifest start_url mismatch');

  const b4html=read(B4+'/index.html');
  const b4style=(b4html.match(/<style id="dark-mode-contrast-closure-v120">([\s\S]*?)<\/style>/)||[])[1];
  const b5style=(html.match(/<style id="dark-mode-contrast-closure-v120">([\s\S]*?)<\/style>/)||[])[1];
  report.protected.darkClosureStyleByteIdentical=b4style===b5style;
  if(!report.protected.darkClosureStyleByteIdentical)report.hardFailures.push('dark-mode CSS changed B4 to B5');
  const beforeTree=new Map(fs.readdirSync(B4).map(f=>[f,shaHex(fs.readFileSync(B4+'/'+f))]));
  const afterTree=new Map(fs.readdirSync(C).map(f=>[f,shaHex(fs.readFileSync(C+'/'+f))]));
  report.protected.changedFiles=[...afterTree.keys()].filter(f=>beforeTree.get(f)!==afterTree.get(f));
  report.protected.unchangedFiles=[...afterTree.keys()].filter(f=>beforeTree.get(f)===afterTree.get(f));
  const allowed=new Set(['index.html','luisa_24_heures.html','manifest.json','sw.js','version.json']);
  if(report.protected.changedFiles.some(f=>!allowed.has(f)))report.hardFailures.push('unexpected B4 to B5 changed files '+report.protected.changedFiles.join(','));
  const markers=[['const CORPUS','const PRAYERS'],['const PROVENANCE_PUBLIC_PROJECTION','function normalizeFrenchSearch'],['function normalizeFrenchSearch','function buildStableSearchDeepLink']];
  report.protected.semanticSegments=[];
  for(const pair of markers){
    const a=pair[0],b=pair[1],s1=b4html.indexOf(a),e1=b4html.indexOf(b),s2=html.indexOf(a),e2=html.indexOf(b);
    const equal=s1>=0&&e1>s1&&s2>=0&&e2>s2&&b4html.slice(s1,e1)===html.slice(s2,e2);
    report.protected.semanticSegments.push({a,b,equal});
    if(!equal)report.hardFailures.push('protected semantic segment changed '+a+' to '+b);
  }
}
async function scanPage(page){
  return await page.evaluate(()=>{
    const parse=s=>{const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/,\s*/).map(Number);return {r:p[0],g:p[1],b:p[2],a:p[3]===undefined?1:p[3]}};
    const visible=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)>0};
    const comp=(fg,bg)=>({r:fg.r*fg.a+bg.r*(1-fg.a),g:fg.g*fg.a+bg.g*(1-fg.a),b:fg.b*fg.a+bg.b*(1-fg.a),a:1});
    const bgFor=el=>{let cur=el,acc={r:255,g:255,b:255,a:1};while(cur){const s=getComputedStyle(cur);if(s.backgroundImage&&s.backgroundImage!=='none')return {skip:true};const c=parse(s.backgroundColor);if(c&&c.a>0){acc=comp(c,acc);if(c.a>=.999)return {color:acc}}cur=cur.parentElement}return {color:acc}};
    const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)};
    const ratio=(a,b)=>{const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)};
    const key=el=>el.id?('#'+el.id):(el.tagName.toLowerCase()+[...el.classList].slice(0,3).map(x=>'.'+x).join(''));
    const lows=[];
    for(const el of document.querySelectorAll('body *')){
      if(!visible(el))continue;
      const txt=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
      if(!txt)continue;
      const s=getComputedStyle(el),fg=parse(s.color),bg=bgFor(el);if(!fg||bg.skip)continue;
      const cr=ratio(fg,bg.color),size=parseFloat(s.fontSize),weight=parseInt(s.fontWeight)||400,large=size>=24||(size>=18.66&&weight>=700),need=large?3:4.5;
      if(cr+.01<need)lows.push({sel:key(el),text:txt.slice(0,100),ratio:+cr.toFixed(2),need,color:s.color,bg:s.backgroundColor,size,weight});
    }
    return {lows,overflow:{scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,bodyScrollWidth:document.body.scrollWidth},theme:document.documentElement.getAttribute('data-theme'),view:typeof state!=='undefined'?state.view:null};
  });
}
async function setView(page,mode,view){
  await page.evaluate(args=>{
    state.themePreference=args.mode;if(typeof applyTheme==='function')applyTheme();
    if(document.getElementById('helpModalOverlay')&&typeof closeHelpModal==='function')closeHelpModal();
    if(document.getElementById('stage6mSettingsOverlay')&&typeof closeSettingsSheet==='function')closeSettingsSheet();
    if(args.view==='home')showHome();
    else if(args.view==='hours')showHoursView(false);
    else if(args.view==='search')showSearchView(false);
    else if(args.view==='espace')showEspaceView(false);
    else if(args.view==='reader')openHour(1,false,{resume:false});
    else if(args.view==='help'){showHome();showHelp();}
    else if(args.view==='settings'){showHome();showSettingsSheet();}
    else if(args.view==='prayer')openPrayer(CORPUS.prayers[0].prayer_id,false);
    else if(args.view==='section')openSection(CORPUS.sections[0].section_id,false);
  },{mode,view});
  await page.waitForTimeout(150);
}
async function targetInfo(page,sel){
  return await page.evaluate(sel=>{
    const parse=s=>{const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/,\s*/).map(Number);return {r:p[0],g:p[1],b:p[2],a:p[3]===undefined?1:p[3]}};
    const comp=(fg,bg)=>({r:fg.r*fg.a+bg.r*(1-fg.a),g:fg.g*fg.a+bg.g*(1-fg.a),b:fg.b*fg.a+bg.b*(1-fg.a),a:1});
    const lum=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)};
    const ratio=(a,b)=>{const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)};
    const e=document.querySelector(sel);if(!e)return null;const s=getComputedStyle(e),r=e.getBoundingClientRect();if(r.width<=0||r.height<=0)return {hidden:true};
    const fg=parse(s.color);let cur=e,bg={r:255,g:255,b:255,a:1},gradient=false;
    while(cur){const cs=getComputedStyle(cur);if(cs.backgroundImage&&cs.backgroundImage!=='none'){gradient=true;break}const c=parse(cs.backgroundColor);if(c&&c.a>0){bg=comp(c,bg);if(c.a>=.999)break}cur=cur.parentElement}
    return {text:e.textContent.trim().replace(/\s+/g,' ').slice(0,120),color:s.color,background:s.backgroundColor,border:s.borderColor,ratio:fg&&!gradient?+ratio(fg,bg).toFixed(2):null,gradient,rect:{x:r.x,y:r.y,w:r.width,h:r.height}};
  },sel);
}
async function browserCampaign(browser){
  const vps=[{name:'iphone',width:390,height:844},{name:'ipad',width:820,height:1180}];
  for(const vp of vps){
    for(const mode of ['dark','system']){
      const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height},colorScheme:'dark'});
      await ctx.addInitScript(()=>{try{localStorage.setItem('lp24_onboarded','1');localStorage.setItem('blind_b5_sentinel','keep')}catch(e){}});
      const page=await ctx.newPage(),consoleErrors=[],pageErrors=[];
      page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
      page.on('pageerror',e=>pageErrors.push(String(e)));
      const res=await page.goto('http://127.0.0.1:8080/'+C+'/luisa_24_heures.html',{waitUntil:'domcontentloaded',timeout:30000});
      await page.waitForFunction(()=>typeof showHome==='function'&&typeof state==='object'&&window.__lp24Init==='done',{timeout:30000});
      const identity=await page.evaluate(()=>({version:APP_VERSION,revision:BUILD_REVISION,sequence:APP_RELEASE_SEQUENCE,releaseId:APP_RELEASE_ID}));
      if(identity.version!==EXPECT.version||identity.revision!==EXPECT.revision||identity.sequence!==EXPECT.sequence||identity.releaseId!==EXPECT.releaseId)report.hardFailures.push('runtime identity mismatch '+vp.name+' '+mode);
      for(const view of ['home','hours','search','espace','reader','help','settings','prayer','section']){
        await setView(page,mode,view);
        const scan=await scanPage(page);
        report.browser.push({vp:vp.name,mode,view,status:res.status(),identity,scan});
        if(scan.overflow.scrollWidth>scan.overflow.clientWidth+1)report.hardFailures.push('horizontal overflow '+vp.name+' '+mode+' '+view+' '+JSON.stringify(scan.overflow));
        await page.screenshot({path:OUT+'/'+vp.name+'_'+mode+'_'+view+'.png',fullPage:false});
      }
      await setView(page,mode,'home');
      const homeDesc=await targetInfo(page,'.stage6m-home-action .d');
      const gear=await targetInfo(page,'#stage6mSettingsBtn');
      const navActive=await targetInfo(page,'.bottom-nav .bn-item.active');
      const navInactive=await targetInfo(page,'.bottom-nav .bn-item:not(.active)');
      await setView(page,mode,'search');
      const activeFilter=await targetInfo(page,'.sf-btn.active');
      const badges={};
      for(const q of ['Jésus','amour','prière','souffrance','coeur','heure']){
        await page.fill('.search-input',q);
        await page.evaluate(()=>{const e=document.querySelector('.search-input');if(typeof onSearchInput==='function')onSearchInput(e)});
        await page.waitForTimeout(100);
        if(!badges.reflection){const x=await targetInfo(page,'.sr-badge.reflection');if(x&&!x.hidden)badges.reflection={q,...x}}
        if(!badges.speech){const x=await targetInfo(page,'.sr-badge.speech');if(x&&!x.hidden)badges.speech={q,...x}}
        if(badges.reflection&&badges.speech)break;
      }
      const navSem=[];
      if(vp.width<=768){
        for(const id of ['bnHome','bnHours','bnSearch','bnEspace']){
          await page.click('#'+id);await page.waitForTimeout(70);
          navSem.push(await page.evaluate(id=>({id,active:[...document.querySelectorAll('.bn-item.active')].map(e=>e.id),current:[...document.querySelectorAll('.bn-item[aria-current="page"]')].map(e=>e.id),view:state.view}),id));
        }
        if(navSem.some(n=>n.active.length!==1||n.current.length!==1||n.active[0]!==n.id||n.current[0]!==n.id))report.hardFailures.push('bottom nav semantics '+vp.name+' '+mode+' '+JSON.stringify(navSem));
      }
      await setView(page,mode,'help');
      const helpText=await page.locator('#helpModalOverlay').innerText();
      const helpHasB5=/Révision technique\s*:\s*B5/i.test(helpText);
      if(!helpHasB5)report.hardFailures.push('Help does not identify B5 '+vp.name+' '+mode);
      report.targets.push({vp:vp.name,mode,homeDesc,gear,navActive,navInactive,activeFilter,badges,navSem,helpHasB5,consoleErrors:[...new Set(consoleErrors)],pageErrors:[...new Set(pageErrors)]});
      for(const item of [['homeDesc',homeDesc],['activeFilter',activeFilter],['reflection',badges.reflection],['speech',badges.speech]]){
        const name=item[0],t=item[1];if(!t||t.hidden||t.ratio===null||t.ratio+0.01<4.5)report.hardFailures.push('target contrast '+name+' '+vp.name+' '+mode+' '+JSON.stringify(t));
      }
      if(vp.width<=768){
        for(const item of [['navActive',navActive],['navInactive',navInactive]]){const name=item[0],t=item[1];if(!t||t.hidden||t.ratio===null||t.ratio+0.01<4.5)report.hardFailures.push('target contrast '+name+' '+vp.name+' '+mode+' '+JSON.stringify(t))}
      }
      if(consoleErrors.length)report.hardFailures.push('console errors '+vp.name+' '+mode+': '+[...new Set(consoleErrors)].join(' | '));
      if(pageErrors.length)report.hardFailures.push('page errors '+vp.name+' '+mode+': '+[...new Set(pageErrors)].join(' | '));
      if(await page.evaluate(()=>localStorage.getItem('blind_b5_sentinel'))!=='keep')report.hardFailures.push('sentinel lost '+vp.name+' '+mode);
      await ctx.close();
    }
  }
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'}),page=await ctx.newPage();
  await page.goto('http://127.0.0.1:8080/'+C+'/luisa_24_heures.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  await page.evaluate(()=>{state.themePreference='dark';applyTheme();showHome()});await page.waitForTimeout(120);
  const onboarding=await targetInfo(page,'.onboarding-primary');report.targets.push({vp:'iphone-first-time',mode:'dark',onboarding});
  if(!onboarding||onboarding.hidden||onboarding.ratio===null||onboarding.ratio+0.01<4.5)report.hardFailures.push('onboarding primary contrast '+JSON.stringify(onboarding));
  await ctx.close();
}
async function focusForced(browser){
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  await ctx.addInitScript(()=>{try{localStorage.setItem('lp24_onboarded','1')}catch(e){}});
  const page=await ctx.newPage();await page.goto('http://127.0.0.1:8080/'+C+'/luisa_24_heures.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  const seq=[];for(let i=0;i<20;i++){await page.keyboard.press('Tab');const x=await page.evaluate(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const s=getComputedStyle(e);return {tag:e.tagName,id:e.id,cls:String(e.className),label:e.getAttribute('aria-label')||e.textContent.trim().replace(/\s+/g,' ').slice(0,60),outlineWidth:s.outlineWidth,outlineStyle:s.outlineStyle,outlineColor:s.outlineColor}});if(x)seq.push(x)}
  report.focus.tabSequence=seq;if(seq.length<5)report.hardFailures.push('focus sequence too short');await ctx.close();

  const fc=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark',forcedColors:'active'});
  await fc.addInitScript(()=>{try{localStorage.setItem('lp24_onboarded','1')}catch(e){}});
  const fp=await fc.newPage();await fp.goto('http://127.0.0.1:8080/'+C+'/luisa_24_heures.html',{waitUntil:'domcontentloaded'});await fp.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  report.forcedColors=await fp.evaluate(()=>{const e=document.querySelector('.bn-item.active'),s=e&&getComputedStyle(e);return {activeNavBorder:s?{width:s.borderWidth,style:s.borderStyle,color:s.borderColor}:null,visibleButtons:[...document.querySelectorAll('button')].filter(x=>{const r=x.getBoundingClientRect();return r.width>0&&r.height>0}).length}});
  if(!report.forcedColors.activeNavBorder||parseFloat(report.forcedColors.activeNavBorder.width)<1)report.hardFailures.push('forced-colors active nav boundary missing');await fc.close();
}
async function workerReply(page,which,data,timeout){
  return await page.evaluate(async args=>{
    const reg=await navigator.serviceWorker.getRegistration(),w=args.which==='waiting'?reg.waiting:args.which==='installing'?reg.installing:reg.active;if(!w)return {error:'worker_missing_'+args.which};
    return await new Promise(resolve=>{const ch=new MessageChannel();let done=false;const t=setTimeout(()=>{if(!done){done=true;resolve({error:'timeout'})}},args.timeout||5000);ch.port1.onmessage=e=>{if(!done){done=true;clearTimeout(t);resolve(e.data)}};w.postMessage(args.data,[ch.port2])});
  },{which,data,timeout});
}
async function cleanPwa(browser){
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'}),page=await ctx.newPage(),errs=[];page.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await page.goto('http://127.0.0.1:8080/'+C+'/luisa_24_heures.html',{waitUntil:'networkidle',timeout:30000});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  const reg=await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return {scope:r.scope,active:r.active&&r.active.state,script:r.active&&r.active.scriptURL,controller:!!navigator.serviceWorker.controller}});
  const rel=await workerReply(page,'active',{type:'GET_RELEASE_INFO_V2'},5000);
  await page.evaluate(async()=>{localStorage.setItem('clean_pwa_sentinel','keep');if(!state.readHours.has(1))await markMeditee(1)});await page.waitForTimeout(500);
  const before=await page.evaluate(async()=>({sentinel:localStorage.getItem('clean_pwa_sentinel'),read1:state.readHours.has(1),snapshot:(await readLatestDurablePersonalSnapshotStrong()).readHours||[]}));
  await page.reload({waitUntil:'networkidle'});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  const after=await page.evaluate(()=>({sentinel:localStorage.getItem('clean_pwa_sentinel'),read1:state.readHours.has(1),v:APP_VERSION,b:BUILD_REVISION,rid:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE}));
  await ctx.setOffline(true);let offline={ok:false};try{await page.reload({waitUntil:'domcontentloaded',timeout:15000});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done',{timeout:10000});offline=await page.evaluate(()=>({ok:true,sentinel:localStorage.getItem('clean_pwa_sentinel'),read1:state.readHours.has(1),text:document.body.innerText.slice(0,100)}))}catch(e){offline={ok:false,error:String(e))}
  report.cleanPwa={reg,rel,before,after,offline,consoleErrors:[...new Set(errs)]};
  if(reg.active!=='activated'||rel.release_id!==EXPECT.releaseId||rel.build_revision!==EXPECT.revision||rel.release_sequence!==EXPECT.sequence)report.hardFailures.push('clean PWA identity '+JSON.stringify(report.cleanPwa));
  if(!after.read1||after.sentinel!=='keep'||!offline.ok||!offline.read1||offline.sentinel!=='keep')report.hardFailures.push('clean PWA persistence/offline '+JSON.stringify(report.cleanPwa));
  if(errs.length)report.hardFailures.push('clean PWA console errors '+[...new Set(errs)].join(' | '));await ctx.close();
}
function resetDir(dst,src){fs.rmSync(dst,{recursive:true,force:true});fs.cpSync(src,dst,{recursive:true})}
async function updatePwa(browser){
  const TEMP='24h-blind-update-scope';resetDir(TEMP,V119);
  const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'}),page=await ctx.newPage(),errs=[];page.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await page.goto('http://127.0.0.1:8080/'+TEMP+'/luisa_24_heures.html',{waitUntil:'networkidle',timeout:30000});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  await page.evaluate(async()=>{localStorage.setItem('update_pwa_sentinel','keep');if(!state.readHours.has(2))await markMeditee(2)});await page.waitForTimeout(500);
  const reg0=await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return {scope:r.scope,active:r.active&&r.active.state,script:r.active&&r.active.scriptURL}});
  const rel0=await workerReply(page,'active',{type:'GET_RELEASE_INFO_V2'},5000);
  resetDir(TEMP,C);
  const updateState=await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update();const deadline=Date.now()+12000;while(Date.now()<deadline&&!r.waiting){await new Promise(x=>setTimeout(x,100))}return {waiting:!!r.waiting,installing:r.installing&&r.installing.state,active:r.active&&r.active.state}});
  const waitingRel=await workerReply(page,'waiting',{type:'GET_RELEASE_INFO_V2'},5000);
  const req='blind-b5-'+Date.now();
  const accepted=await workerReply(page,'waiting',{type:'ACTIVATE_UPDATE_V2',expected_release_id:EXPECT.releaseId,expected_release_sequence:EXPECT.sequence,request_id:req},8000);
  const activated=await page.evaluate(async expected=>{const deadline=Date.now()+12000;while(Date.now()<deadline){const r=await navigator.serviceWorker.getRegistration();if(r.active&&!r.waiting){const data=await new Promise(resolve=>{const ch=new MessageChannel(),t=setTimeout(()=>resolve(null),1200);ch.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};r.active.postMessage({type:'GET_RELEASE_INFO_V2'},[ch.port2])});if(data&&data.release_id===expected)return {ok:true,data,controller:!!navigator.serviceWorker.controller}}await new Promise(x=>setTimeout(x,100))}return {ok:false}},EXPECT.releaseId);
  await page.reload({waitUntil:'networkidle',timeout:30000});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done');
  const after=await page.evaluate(()=>({v:APP_VERSION,b:BUILD_REVISION,rid:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,sentinel:localStorage.getItem('update_pwa_sentinel'),read2:state.readHours.has(2)}));
  await ctx.setOffline(true);let offline={ok:false};try{await page.reload({waitUntil:'domcontentloaded',timeout:15000});await page.waitForFunction(()=>typeof showHome==='function'&&window.__lp24Init==='done',{timeout:10000});offline=await page.evaluate(()=>({ok:true,v:APP_VERSION,b:BUILD_REVISION,rid:APP_RELEASE_ID,seq:APP_RELEASE_SEQUENCE,sentinel:localStorage.getItem('update_pwa_sentinel'),read2:state.readHours.has(2)}))}catch(e){offline={ok:false,error:String(e))}
  report.updatePwa={reg0,rel0,updateState,waitingRel,accepted,activated,after,offline,consoleErrors:[...new Set(errs)]};
  if(rel0.release_id!=='24h-v119-b1-20261001-adversarial-ux-correction')report.hardFailures.push('update predecessor identity '+JSON.stringify(rel0));
  if(!updateState.waiting||waitingRel.release_id!==EXPECT.releaseId||accepted.type!=='ACTIVATE_UPDATE_ACCEPTED_V2'||!activated.ok)report.hardFailures.push('explicit update activation '+JSON.stringify(report.updatePwa));
  if(after.rid!==EXPECT.releaseId||after.b!==EXPECT.revision||after.sentinel!=='keep'||!after.read2||!offline.ok||offline.sentinel!=='keep'||!offline.read2)report.hardFailures.push('update continuity '+JSON.stringify(report.updatePwa));
  if(errs.length)report.hardFailures.push('update PWA console errors '+[...new Set(errs)].join(' | '));await ctx.close();fs.rmSync(TEMP,{recursive:true,force:true});
}
(async()=>{
  staticAudit();
  const browser=await chromium.launch({headless:true});
  await browserCampaign(browser);
  await focusForced(browser);
  await cleanPwa(browser);
  await updatePwa(browser);
  await browser.close();
  report.broadLowContrast=report.browser.flatMap(r=>r.scan.lows.map(x=>Object.assign({ctx:r.vp+'/'+r.mode+'/'+r.view},x)));
  report.summary={hardFailureCount:report.hardFailures.length,broadLowContrastCount:report.broadLowContrast.length,static:report.static,protected:report.protected,cleanPwa:report.cleanPwa,updatePwa:report.updatePwa};
  fs.writeFileSync(OUT+'/REPORT.json',JSON.stringify(report,null,2));fs.writeFileSync(OUT+'/SUMMARY.json',JSON.stringify(report.summary,null,2));
  console.log(JSON.stringify(report.summary,null,2));
  if(report.hardFailures.length){console.error('B5_BLIND_ADVERSARIAL_FAIL',JSON.stringify(report.hardFailures,null,2));process.exit(2)}
  console.log('B5_BLIND_ADVERSARIAL_MACHINE_PASS');
})().catch(e=>{try{fs.writeFileSync(OUT+'/HARNESS_FATAL.txt',String(e&&e.stack||e))}catch(_){};console.error(e);process.exit(1)});