const { chromium, webkit } = require('playwright');
const fs = require('fs');
const assert = (c,m)=>{ if(!c) throw new Error(m); };
const results=[];
function rec(name,detail){results.push({name,ok:true,detail}); console.log('PASS',name,JSON.stringify(detail??null));}
function rgba(s){const m=String(s).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/);return m?[+m[1],+m[2],+m[3],m[4]===undefined?1:+m[4]]:null}
function lum(c){return c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0)}
function contrast(a,b){const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)}
function composite(f,b){return [0,1,2].map(i=>f[i]*f[3]+b[i]*(1-f[3]))}
async function ratio(page,sel,bgSel){
  const x=await page.locator(sel).evaluate((e,bgSel)=>{const c=getComputedStyle(e),b=bgSel?getComputedStyle(document.querySelector(bgSel)):getComputedStyle(e.parentElement);return {c:c.color,b:c.backgroundColor==='rgba(0, 0, 0, 0)'?b.backgroundColor:c.backgroundColor,op:+c.opacity}},bgSel);
  let fg=rgba(x.c),bg=rgba(x.b); if(!fg||!bg) throw new Error('unparsed colour '+JSON.stringify(x));
  if(fg[3]<1) fg=[...composite(fg,bg),1];
  if(x.op<1) fg=[...composite([...fg.slice(0,3),x.op],bg),1];
  return {ratio:contrast(fg,bg),raw:x};
}
function trap(page,label){
  const errs=[]; page.on('pageerror',e=>errs.push('page:'+e.message)); page.on('console',m=>{if(m.type()==='error')errs.push('console:'+m.text())});
  return ()=>{assert(errs.length===0,label+' errors '+JSON.stringify(errs));rec(label+':no_runtime_errors',[])}
}
async function readyL(p){await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='2.15'&&typeof CORPUS!=='undefined'&&CORPUS.length===136,{timeout:30000});}
async function readyM(p){await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='49'&&typeof State!=='undefined'&&State.corpus?.length===37&&!document.getElementById('screen-loading').classList.contains('active'),{timeout:30000});}

async function lettres(bt,bname){
  const browser=await bt.launch();
  // Mobile normal + actual export + search.
  let c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'light',acceptDownloads:true});
  await c.addInitScript(()=>localStorage.setItem('lp_onboarded','1'));
  let p=await c.newPage(), done=trap(p,'L:'+bname+':mobile');
  await p.goto('http://127.0.0.1:8141/',{waitUntil:'domcontentloaded'}); await readyL(p);
  assert(await p.locator('#list-title').textContent()==='136 Lettres','L list count label');
  await p.locator('#home-settings-btn').click();
  await p.locator('#settings-export-btn').waitFor({state:'visible'});
  let r=await ratio(p,'#settings-export-btn'); assert(r.ratio>=4.5,'L export normal contrast '+r.ratio); rec('L:'+bname+':export_normal_contrast',r.ratio);
  await p.locator('#settings-export-btn').hover(); r=await ratio(p,'#settings-export-btn'); assert(r.ratio>=4.5,'L export hover contrast '+r.ratio); rec('L:'+bname+':export_hover_contrast',r.ratio);
  const dlPromise=p.waitForEvent('download'); await p.locator('#settings-export-btn').click(); const dl=await dlPromise; const fp=await dl.path(); const env=JSON.parse(fs.readFileSync(fp,'utf8'));
  assert(env.format==='luisa-letters-user-data'&&env.app_version==='2.15'&&env.corpus.total_letters===136,'L export envelope '+JSON.stringify({format:env.format,app_version:env.app_version,letters:env.corpus?.total_letters}));
  rec('L:'+bname+':actual_backup_download',{format:env.format,app_version:env.app_version,letters:env.corpus.total_letters});
  await p.locator('.settings-close').click(); await p.locator('#pnav-search').click(); await p.locator('#search-input').fill('volonté');
  await p.waitForFunction(()=>document.querySelectorAll('#search-results .search-result-control').length>0); const n=await p.locator('#search-results .search-result-control').count(); rec('L:'+bname+':search_from_fresh_ui',n);
  done(); await c.close();

  // System dark theme and repaired states.
  c=await browser.newContext({viewport:{width:820,height:1180},colorScheme:'dark'});
  await c.addInitScript(()=>{localStorage.setItem('lp_onboarded','1');localStorage.setItem('lp_theme','system');localStorage.setItem('lp_read','[1]')});
  p=await c.newPage(); done=trap(p,'L:'+bname+':wide_system_dark'); await p.goto('http://127.0.0.1:8141/',{waitUntil:'domcontentloaded'}); await readyL(p);
  await p.locator('#snav-settings').click(); r=await ratio(p,'#settings-export-btn'); assert(r.ratio>=4.5,'L system-dark export '+r.ratio);
  rec('L:'+bname+':system_dark_export',r.ratio);
  const build=await ratio(p,'#sidebar .build-meta','#sidebar'); assert(build.ratio>=4.5,'L build metadata contrast '+build.ratio); rec('L:'+bname+':wide_build_metadata',build.ratio);
  done(); await c.close();

  // Corrupt/stale persisted values must not brick startup.
  c=await browser.newContext({viewport:{width:390,height:844}});
  await c.addInitScript(()=>{localStorage.setItem('lp_onboarded','1');localStorage.setItem('lp_favs','{bad');localStorage.setItem('lp_theme','nonsense');localStorage.setItem('lp_size','gigantic')});
  p=await c.newPage(); done=trap(p,'L:'+bname+':corrupt_storage'); await p.goto('http://127.0.0.1:8141/',{waitUntil:'domcontentloaded'}); await readyL(p);
  const st=await p.evaluate(()=>({theme:document.documentElement.dataset.theme,size:document.documentElement.dataset.textLevel,letters:CORPUS.length}));
  assert(st.letters===136&&['system','light','dark'].includes(st.theme)&&['small','normal','large','xlarge'].includes(st.size),'L corrupt storage recovery '+JSON.stringify(st));rec('L:'+bname+':corrupt_storage_recovery',st);done();await c.close();
  await browser.close();
}

async function marie(bt,bname){
  const browser=await bt.launch();
  // Mobile system-dark + live OS theme change + search + actual backup/restore preview.
  let c=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark',acceptDownloads:true});
  await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.removeItem('mjv_theme')});
  let p=await c.newPage(),done=trap(p,'M:'+bname+':mobile_system'); await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'}); await readyM(p);
  assert((await p.locator('#mobile-version').textContent()).trim()==='v49','M mobile version');
  let op=+(await p.locator('#dark-toggle-btn').evaluate(e=>getComputedStyle(e).opacity)); assert(op>=.999,'M theme opacity '+op); rec('M:'+bname+':theme_control_opacity',op);
  assert(await p.evaluate(()=>document.documentElement.dataset.theme)==='dark','M initial system dark');
  await p.emulateMedia({colorScheme:'light'}); await p.waitForFunction(()=>!document.documentElement.hasAttribute('data-theme')); rec('M:'+bname+':live_system_theme_switch','dark→system-light(no data-theme attr)');
  await p.locator('#nav-search').click(); await p.locator('#search-input').fill('Fiat'); await p.waitForFunction(()=>document.querySelectorAll('#screen-list .snippet-card').length>0); rec('M:'+bname+':search_fiat',await p.locator('#screen-list .snippet-card').count());
  await p.locator('#nav-espace').click(); await p.waitForTimeout(100);
  const saveBtn=p.locator('.backup-btn.primary').first(); await saveBtn.waitFor({state:'visible'});
  const dlPromise=p.waitForEvent('download'); await saveBtn.click(); const dl=await dlPromise; const fp=await dl.path(); const env=JSON.parse(fs.readFileSync(fp,'utf8'));
  assert(env.format==='MJV_LOCAL_BACKUP'&&String(env.app.version)==='49'&&env.corpus.units===37&&env.corpus.paragraphs===753,'M backup '+JSON.stringify({format:env.format,app:env.app,corpus:env.corpus}));
  rec('M:'+bname+':actual_backup_download',{format:env.format,version:env.app.version,units:env.corpus.units,paragraphs:env.corpus.paragraphs});
  await p.locator('#backup-file-input').setInputFiles(fp); await p.locator('#restore-modal').waitFor({state:'visible'});
  const wr=await ratio(p,'.restore-warning','#restore-modal .modal-box'); assert(wr.ratio>=4.5,'M restore warning '+wr.ratio); rec('M:'+bname+':restore_warning_contrast',wr.ratio);
  await p.locator('#restore-confirm-btn').hover(); const sr=await ratio(p,'#restore-confirm-btn'); assert(sr.ratio>=4.5,'M restore confirm hover '+sr.ratio); rec('M:'+bname+':restore_confirm_hover',sr.ratio);
  done();await c.close();

  // Wide dark: version badge + theme control.
  c=await browser.newContext({viewport:{width:820,height:1180},colorScheme:'dark'}); await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
  p=await c.newPage();done=trap(p,'M:'+bname+':wide_dark');await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});await readyM(p);
  const vr=await ratio(p,'#desktop-version','.wide-topbar');assert(vr.ratio>=4.5,'M badge '+vr.ratio);rec('M:'+bname+':wide_version_badge',vr.ratio);
  op=+(await p.locator('#wnav-dark').evaluate(e=>getComputedStyle(e).opacity));assert(op>=.999,'M wide theme opacity '+op);rec('M:'+bname+':wide_theme_control_opacity',op);done();await c.close();

  // Malformed stored state should degrade safely, not brick the shell.
  c=await browser.newContext({viewport:{width:390,height:844}}); await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_notes','{bad');localStorage.setItem('mjv_highlights','[]bad');localStorage.setItem('mjv_theme','bogus')});
  p=await c.newPage();done=trap(p,'M:'+bname+':corrupt_storage');await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});await readyM(p);
  const st=await p.evaluate(()=>({version:APP_VERSION,units:State.corpus.length,theme:State.themeMode}));assert(st.version==='49'&&st.units===37&&['system','light','dark'].includes(st.theme),'M corrupt state '+JSON.stringify(st));rec('M:'+bname+':corrupt_storage_recovery',st);done();await c.close();
  await browser.close();
}

(async()=>{
  for(const [bt,n] of [[chromium,'chromium'],[webkit,'webkit']]){await lettres(bt,n);await marie(bt,n);}
  fs.writeFileSync('/tmp/INDEPENDENT_BLIND_CHALLENGE_CURRENT_2026-10-05.json',JSON.stringify({status:'PASS',results},null,2));
  console.log('BLIND_CHALLENGE_PASS',results.length);
})().catch(e=>{console.error('BLIND_CHALLENGE_FAIL',e);process.exit(2)});