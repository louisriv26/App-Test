const { chromium, webkit } = require('playwright');
const fs=require('fs');
const ROOT='marie-v50-test';
const BASE='http://127.0.0.1:8150/'+ROOT+'/';
const results=[];
function pass(name,detail){results.push({name,status:'PASS',detail});console.log('PASS',name,JSON.stringify(detail??null));}
function assert(c,m){if(!c)throw new Error(m)}
function capture(p,label){const errs=[];p.on('pageerror',e=>errs.push('PAGE '+String(e)));p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});return()=>{const bad=errs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));assert(!bad.length,label+' runtime errors '+JSON.stringify(bad));pass(label+':runtime_errors',[])}}
async function ready(p){await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='50'&&State?.corpus?.length===37&&!document.getElementById('screen-loading').classList.contains('active'),null,{timeout:30000})}
async function geom(p){
 return p.evaluate(()=>{const g=s=>{const e=document.querySelector(s);const r=e.getBoundingClientRect();return{top:r.top,bottom:r.bottom,height:r.height,client:e.clientHeight,scroll:e.scrollHeight,display:getComputedStyle(e).display,max:getComputedStyle(e).maxHeight,flex:getComputedStyle(e).flex}};const sb=g('#wide-sidebar'),c=g('#ws-today-card'),o=g('.ws-today-oraison'),n=g('#wide-reader-nav');const vis=Math.max(0,Math.min(c.bottom,o.bottom)-Math.max(c.top,o.top));return{sb,c,o,n,free:sb.bottom-c.bottom,overflow:Math.max(0,c.scroll-c.client),fraction:o.height?vis/o.height:1,wide:getComputedStyle(document.getElementById('wide-shell')).display!=='none'}});
}
async function longestDay(p){return p.evaluate(()=>{let best=null;for(const u of State.corpus){if(!u.day_number||u.day_number>31)continue;const d=App.getTodayData(u);const len=(d?.pratique?.length||0)+(d?.oraison?.length||0);if(!best||len>best.len)best={day:u.day_number,len,ordinal:d?.ordinal};}return best})}

async function wideChallenge(bt,engine){
 const b=await bt.launch();
 // A. Screenshot-derived geometry + live text-size transitions + day nav + modal.
 let c=await b.newContext({viewport:{width:1215,height:751},colorScheme:'dark'});
 await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
 let p=await c.newPage(),done=capture(p,'wide:'+engine);
 await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);
 const self=await p.evaluate(()=>App.selfTest());assert(self.total===156&&self.passed===156&&!self.failed.length,'selfTest '+JSON.stringify(self));pass(engine+':selftest',self);
 await p.evaluate(()=>App.openDay(5));
 for(const level of ['normal','large','xlarge','normal']){
   await p.evaluate(l=>App.applyTextSize(l,false),level);await p.waitForTimeout(50);
   const m=await geom(p);
   assert(m.wide,'not wide '+level);assert(Math.abs(m.free)<=1.5,'free space '+level+' '+m.free);assert(m.c.max==='none'&&m.c.flex==='1 1 auto','computed repair '+JSON.stringify(m.c));
   if(level==='large'||level==='xlarge'){assert(m.overflow<=1,'screenshot geometry still scrolls '+level+' '+m.overflow);assert(m.fraction>=.999,'oraison clipped '+level+' '+m.fraction)}
   pass(engine+':screenshot:'+level,{free:m.free,overflow:m.overflow,fraction:m.fraction});
 }
 await p.locator('#wide-next').click();await p.waitForFunction(()=>State.activeDay===6);assert((await p.locator('#wide-reader-day-badge').innerText()).includes('6'),'next day badge');pass(engine+':wide_next_day',6);
 await p.locator('#ws-today-card').click();await p.waitForSelector('#today-modal.open');const modal=await p.locator('#today-modal').innerText();assert(/Oraison jaculatoire/i.test(modal),'today modal missing oraison');pass(engine+':today_modal_open',modal.length);await p.locator('#today-modal-close').click();
 // Search interaction then return to Jours.
 await p.locator('#wnav-search').click();await p.fill('#wide-search-input','Fiat');await p.waitForSelector('#wide-list-scroll .snippet-card');const count=await p.locator('#wide-list-scroll .snippet-card').count();assert(count>0,'search empty');await p.locator('#wide-list-scroll .snippet-card').first().click();await p.waitForFunction(()=>document.getElementById('wide-reader-content').style.display!=='none');await p.locator('#wnav-jours').click();await p.waitForFunction(()=>document.getElementById('wide-sidebar').dataset.mode==='jours');const mback=await geom(p);assert(Math.abs(mback.free)<=1.5,'jour return geometry '+mback.free);pass(engine+':search_to_reader_to_jours',{results:count,free:mback.free});
 done();await c.close();

 // B. Legitimate overflow on short wide viewport must consume all space and be fully scroll-accessible.
 c=await b.newContext({viewport:{width:768,height:600},colorScheme:'light'});
 await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light')});
 p=await c.newPage();done=capture(p,'short:'+engine);await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);
 const long=await longestDay(p);await p.evaluate(d=>App.openDay(d),long.day);await p.evaluate(()=>App.applyTextSize('xlarge',false));await p.waitForTimeout(50);
 let m=await geom(p);assert(Math.abs(m.free)<=1.5,'short free '+m.free);assert(m.wide,'768x600 not wide');assert(m.overflow>1,'expected real overflow absent for long day '+JSON.stringify({long,m}));const before=m.fraction;
 await p.locator('#ws-today-card').evaluate(e=>e.scrollTop=e.scrollHeight);await p.waitForTimeout(30);m=await geom(p);assert(m.fraction>=.98,'oraison inaccessible after scroll '+m.fraction);pass(engine+':short_legitimate_scroll',{day:long.day,len:long.len,overflow:m.overflow,beforeFraction:before,afterFraction:m.fraction,free:m.free});
 done();await c.close();

 // C. 1199/1200 breakpoint transition must preserve residual-height invariant.
 for(const width of [1199,1200]){
   c=await b.newContext({viewport:{width,height:750},colorScheme:'light'});await c.addInitScript(()=>localStorage.setItem('mjv_onboarded','1'));
   p=await c.newPage();await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);await p.evaluate(()=>App.openDay(5));await p.evaluate(()=>App.applyTextSize('xlarge',false));await p.waitForTimeout(30);m=await geom(p);
   assert(Math.abs(m.free)<=1.5,'breakpoint '+width+' free '+m.free);pass(engine+':breakpoint:'+width,{free:m.free,overflow:m.overflow,fraction:m.fraction});await c.close();
 }
 await b.close();
}

async function systemThemeChallenge(bt,engine){
 const b=await bt.launch();const c=await b.newContext({viewport:{width:1215,height:751},colorScheme:'dark'});
 await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.removeItem('mjv_theme')});
 const p=await c.newPage(),done=capture(p,'system:'+engine);await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);await p.evaluate(()=>App.openDay(5));await p.evaluate(()=>App.applyTextSize('xlarge',false));
 const dark=await p.evaluate(()=>({theme:document.documentElement.getAttribute('data-theme'),bg:getComputedStyle(document.body).backgroundColor}));
 assert(dark.theme==='dark','system dark unresolved '+JSON.stringify(dark));await p.emulateMedia({colorScheme:'light'});await p.waitForFunction(()=>document.documentElement.getAttribute('data-theme')!=='dark');const light=await p.evaluate(()=>({theme:document.documentElement.getAttribute('data-theme'),bg:getComputedStyle(document.body).backgroundColor}));
 const m=await geom(p);assert(Math.abs(m.free)<=1.5,'system light free '+m.free);pass(engine+':live_system_theme',{dark,light,free:m.free});done();await c.close();await b.close();
}

async function backupOfflineChallenge(){
 const b=await chromium.launch();
 // Actual backup download and restore preview.
 let c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark',acceptDownloads:true});await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
 let p=await c.newPage(),done=capture(p,'backup:chromium');await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);await p.locator('#nav-espace').click();await p.waitForSelector('#screen-espace.active .backup-btn.primary');
 const dlP=p.waitForEvent('download');await p.locator('#screen-espace .backup-btn.primary').first().click();const dl=await dlP,fp=await dl.path();const env=JSON.parse(fs.readFileSync(fp,'utf8'));assert(env.format==='MJV_LOCAL_BACKUP'&&String(env.app.version)==='50'&&env.corpus.units===37&&env.corpus.paragraphs===753,'backup envelope '+JSON.stringify(env.app));pass('chromium:actual_backup',{version:env.app.version,units:env.corpus.units,paragraphs:env.corpus.paragraphs});
 await p.locator('#backup-file-input').setInputFiles(fp);await p.waitForSelector('#restore-modal.open');const summary=await p.locator('#restore-summary').innerText();assert(/Progression/.test(summary)&&/Notes/.test(summary),'restore preview '+summary);pass('chromium:restore_preview',summary.length);await p.locator('#restore-cancel-btn').click().catch(async()=>{await p.evaluate(()=>App.closeRestoreModal())});done();await c.close();

 // Fresh-scope service-worker cache, then real cold offline wide reopen with xlarge geometry.
 c=await b.newContext({viewport:{width:1215,height:751},colorScheme:'light'});await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light');localStorage.setItem('mjv_text_size','xlarge')});
 p=await c.newPage();let errs=[];p.on('pageerror',e=>errs.push(String(e)));await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);await p.waitForFunction(()=>!!navigator.serviceWorker.controller,{timeout:30000}).catch(()=>{});
 await p.evaluate(()=>App.openDay(5));await p.evaluate(()=>App.applyTextSize('xlarge',false));await p.waitForTimeout(1200);const caches=await p.evaluate(()=>caches.keys());assert(caches.some(x=>/-shell-v50$/.test(x)),'v50 shell cache absent '+JSON.stringify(caches));pass('chromium:v50_cache',caches);
 await c.setOffline(true);await p.close();p=await c.newPage();p.on('pageerror',e=>errs.push(String(e)));await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:30000});await ready(p);await p.evaluate(()=>App.openDay(5));const m=await geom(p);assert(Math.abs(m.free)<=1.5&&m.c.max==='none','offline geometry '+JSON.stringify(m));assert(!errs.some(x=>/referenceerror|typeerror|syntaxerror/i.test(x)),'offline errors '+JSON.stringify(errs));pass('chromium:cold_offline_geometry',{free:m.free,overflow:m.overflow,fraction:m.fraction});await c.close();await b.close();
}

async function corruptStateChallenge(){
 const b=await webkit.launch();const c=await b.newContext({viewport:{width:390,height:844}});
 await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_notes','{bad');localStorage.setItem('mjv_highlights','[]bad');localStorage.setItem('mjv_theme','bogus');localStorage.setItem('mjv_text_size','nonsense')});
 const p=await c.newPage(),done=capture(p,'corrupt:webkit');await p.goto(BASE,{waitUntil:'domcontentloaded'});await ready(p);const x=await p.evaluate(()=>({v:APP_VERSION,units:State.corpus.length,theme:State.themeMode,textSize:State.textSize}));assert(x.v==='50'&&x.units===37&&['system','light','dark'].includes(x.theme)&&['small','normal','large','xlarge'].includes(x.textSize),'corrupt recovery '+JSON.stringify(x));pass('webkit:corrupt_storage_recovery',x);done();await c.close();await b.close();
}

(async()=>{
  await wideChallenge(chromium,'chromium');
  await wideChallenge(webkit,'webkit');
  await systemThemeChallenge(chromium,'chromium');
  await systemThemeChallenge(webkit,'webkit');
  await backupOfflineChallenge();
  await corruptStateChallenge();
  fs.writeFileSync('/tmp/MJV_v50_INDEPENDENT_BLIND_AUDIT_2026-10-05.json',JSON.stringify({candidate:'MJV v50',tree:'05f10479d5e9a5e476221cf7881fb5441cf5a909',status:'PASS',assertions:results.length,results},null,2));
  console.log('MJV_V50_INDEPENDENT_BLIND_PASS',results.length);
})().catch(e=>{console.error('MJV_V50_INDEPENDENT_BLIND_FAIL',e);process.exit(2)});