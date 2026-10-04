const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.join(process.cwd(),'ldc-v139-r12-search-v21a-recert');
const URL='http://127.0.0.1:8150/ldc-v139-r12-search-v21a-recert/';
const EXPECT={app:'v2.19.139-R1B-UX-ACCESS-R12',pub:'139',sw:'ldc-v2.19.139-R1B-ux-access-r12',tree:'b9aaaa762034d9a21398bc8c242c802f59062492'};
const out={candidate:'LDC v139 independent re-audit',generated_at:new Date().toISOString(),overall:'UNKNOWN',checks:{},errors:[]};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitReady(p,t=90000){await p.waitForFunction(()=>{const l=document.getElementById('loading'),v=document.getElementById('version-pill-home');return l&&getComputedStyle(l).display==='none'&&v&&v.textContent==='v139';},{timeout:t});}
async function ensureController(p){await p.waitForFunction(()=>navigator.serviceWorker.ready.then(()=>true),{timeout:30000});if(!await p.evaluate(()=>!!navigator.serviceWorker.controller)){await p.reload({waitUntil:'domcontentloaded',timeout:90000});await waitReady(p);}}
async function search(p,term,mode){
  return await p.evaluate(async({term,mode})=>{
    await goSearch(); await setSupplementMode(mode,{rerender:false,silent:true}); renderSearchSourceModeRow();
    const i=document.getElementById('search-input');i.value=term;await runSearch();
    for(let n=0;n<150;n++){const m=document.getElementById('search-meta')?.textContent||'';if(m!=='Recherche…')break;await new Promise(r=>setTimeout(r,100));}
    const meta=document.getElementById('search-meta')?.textContent||'',cards=[...document.querySelectorAll('#search-results .result-card')];
    return{term,mode,meta,cards:cards.length,failed:/indisponible/i.test(meta),source:supplementMode,firstKey:cards[0]?.dataset.resultKey||''};
  },{term,mode});
}
async function run(){
 const profile=path.join(process.cwd(),'.qa-ldc-v139-independent-profile');fs.rmSync(profile,{recursive:true,force:true});
 const c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:1280,height:900}});
 const p=await c.newPage(),pageErrors=[],consoleErrors=[];
 p.on('pageerror',e=>pageErrors.push(String(e)));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 const r=await p.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});await waitReady(p);await ensureController(p);
 const served=crypto.createHash('sha256').update(Buffer.from(await r.body())).digest('hex');
 const local=crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'index.html'))).digest('hex');
 out.checks.identity=await p.evaluate(async()=>{const v=await fetch('./version.json',{cache:'no-store'}).then(r=>r.json()),m=await fetch('./manifest.json',{cache:'no-store'}).then(r=>r.json()),reg=await navigator.serviceWorker.ready;const keys=(await caches.keys()).filter(x=>x.startsWith('ldc-le-livre-du-ciel-')).sort();return{app:APP_VERSION,pub:PUBLIC_VERSION,swExpected:SW_CACHE_VERSION,pill:document.getElementById('version-pill-home')?.textContent||'',version:v.app_version,versionPub:v.public_version,controller:!!navigator.serviceWorker.controller,active:reg.active&&reg.active.scriptURL,caches:keys,manifest:m};});
 out.checks.served={served,local,exact:served===local};

 // Search: three source modes + short token + Unicode normalization
 out.checks.search=[];
 for(const [term,mode] of [['de','aflp'],['de','additions'],['bateau','enriched'],['je','enriched'],['volonte\u0301','enriched']]) out.checks.search.push(await search(p,term,mode));
 await p.evaluate(()=>setSupplementMode('enriched',{rerender:false,silent:true}));

 // Tome -> entry -> next -> back; favorite persistence and list marker
 out.checks.reader=await p.evaluate(async()=>{
   await goTomes(); await openTome(1,{intent:NAV_INTENT.FRESH_TOME});
   const list=document.getElementById('entries-list'),before=list.scrollTop; list.scrollTop=Math.min(420,Math.max(0,list.scrollHeight-list.clientHeight)); const sourceTop=list.scrollTop;
   const first=list.querySelector('.entry-item'); if(!first)throw new Error('no entry row'); const firstId=first.dataset.entryId;
   await openEntryFromEntries(1,firstId,first);
   const opened=currentEntry&&currentEntry.id,readerTop=document.getElementById('reader-scroll')?.scrollTop||0;
   const favBefore=!!(await dbGet('favorites',currentEntry.id)); if(favBefore)await toggleFav(); await toggleFav();
   const favAfter=await dbGet('favorites',currentEntry.id); const pressed=document.getElementById('reader-fav-top')?.getAttribute('aria-pressed');
   const old=currentEntry.id; const nextOk=await navEntry(1); const next=currentEntry&&currentEntry.id;
   await backFromReader();
   const restoredScreen=document.querySelector('.screen.active')?.id||'',restoredTop=document.getElementById('entries-list')?.scrollTop||0;
   const marker=!!document.querySelector('#entry-row-'+CSS.escape(firstId)+' [data-favorite-indicator="true"]');
   return{before,sourceTop,firstId,opened,readerTop,favAfter:!!favAfter,pressed,old,nextOk,next,restoredScreen,restoredTop,marker};
 });

 // Mon Espace favorite visibility, then remove favorite cleanly
 out.checks.espace=await p.evaluate(async()=>{
   await goEspace(); await renderEspace(); showEspaceTab('favorites');
   const panel=document.getElementById('ep-favorites'); const text=panel?.textContent||'',count=panel?.querySelectorAll('[data-filter-text]').length||0;
   const favs=await dbGetAll('favorites');
   if(favs.length){const f=favs[0];await dbDelete('favorites',f.entry_id);}
   await renderEspace(); showEspaceTab('favorites');
   return{text,count,storedBefore:favs.length,storedAfter:(await dbGetAll('favorites')).length};
 });

 // Theme + text level persistence across reload
 out.checks.settings=await p.evaluate(async()=>{
   await setThemePreference('dark'); await setTextLevel('xlarge');
   const theme=await dbGet('settings','theme'),text=await dbGet('settings','textLevel');
   return{theme:theme&&theme.val,text:text&&text.val,htmlTheme:document.documentElement.getAttribute('data-theme'),readerSize:getComputedStyle(document.documentElement).getPropertyValue('--reader-size').trim()};
 });
 await p.reload({waitUntil:'domcontentloaded',timeout:90000});await waitReady(p);await ensureController(p);
 out.checks.settingsReload=await p.evaluate(async()=>({theme:document.documentElement.getAttribute('data-theme'),text:(await dbGet('settings','textLevel'))?.val,themeDb:(await dbGet('settings','theme'))?.val,readerSize:getComputedStyle(document.documentElement).getPropertyValue('--reader-size').trim()}));

 // Help/provenance round trip from non-top scroll
 out.checks.help=await p.evaluate(async()=>{await openHelp();const hs=document.getElementById('help-scroll');hs.scrollTop=Math.min(620,Math.max(0,hs.scrollHeight-hs.clientHeight));const before=hs.scrollTop;await openProvenanceDetails('help');await new Promise(r=>setTimeout(r,200));const ptop=document.getElementById('provenance-scroll')?.scrollTop||0;await closeProvenanceDetails();await new Promise(r=>setTimeout(r,350));return{before,after:hs.scrollTop,provenanceTop:ptop,restored:Math.abs(hs.scrollTop-before)<=3&&ptop<=1};});

 // PWA asset probes
 out.checks.assets=await p.evaluate(async()=>{const urls=['./manifest.json','./sw.js','./assets/fonts/fonts.css','./assets/icons/tabler-icons.min.css','./icons/icon-192.png','./corpus/volume_36.json','./corpus/search_v2_index.json'];const o={};for(const u of urls){try{const r=await fetch(u,{cache:'no-store'});o[u]={ok:r.ok,status:r.status,bytes:(await r.arrayBuffer()).byteLength};}catch(e){o[u]={ok:false,error:String(e)}}}return o;});

 // Responsive smoke in same exact app, new pages/contexts
 const widths=[[390,844],[820,1180],[1440,900]],layouts=[];
 for(const [width,height] of widths){const q=await c.newPage({viewport:{width,height}});await q.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});await waitReady(q);const x=await q.evaluate(()=>({screen:document.querySelector('.screen.active')?.id||'',bodyW:document.body.scrollWidth,innerW:innerWidth,version:document.getElementById('version-pill-home')?.textContent||'',navVisible:getComputedStyle(document.getElementById('bottom-nav')).display!=='none'}));layouts.push({width,height,...x,overflow:x.bodyW>x.innerW+2});await q.close();} out.checks.layouts=layouts;

 // Backup round trip
 out.checks.backup=await p.evaluate(async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));await setThemePreference('dark');const env=await collectUserDataEnvelope();await setThemePreference('light');const prepared=await prepareBackupEnvelopeForImport(env),bytes=new TextEncoder().encode(JSON.stringify(prepared.env)).length,validation=await validateBackupEnvelope(prepared.env,bytes);if(!validation.ok)return{pass:false,errors:validation.errors};pendingBackupImport={kind:'legacy-json',env:prepared.env,validation,fileName:'independent-reaudit.json',migrationSummary:prepared.summary};await confirmImportBackup();let theme=null;for(let i=0;i<40;i++){theme=await dbGet('settings','theme').catch(()=>null);if(theme&&theme.val==='dark')break;await wait(100);}return{pass:!!theme&&theme.val==='dark',theme:theme&&theme.val,warnings:validation.warnings||[]};});

 // Full offline preparation and persisted readiness
 await p.evaluate(()=>startOfflinePreparation()); await p.waitForFunction(()=>typeof offlineUiState!=='undefined'&&['READY','ERROR','PARTIAL','CANCELLED'].includes(offlineUiState.state),{timeout:300000,polling:500});
 let persisted=false;for(let i=0;i<80;i++){persisted=await p.evaluate(async()=>{const s=await dbGet('settings','offline_completion').catch(()=>null);return !!(s&&s.val&&s.val.state==='READY');});if(persisted)break;await sleep(100);}
 out.checks.offline=await p.evaluate(async()=>{const s=await dbGet('settings','offline_completion').catch(()=>null);return{ui:offlineUiState.state,completed:offlineUiState.completed,total:offlineUiState.total,failed:(offlineUiState.failed||[]).length,saved:s&&s.val};});
 await c.close();

 const c2=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:390,height:844}});
 await c2.setOffline(true);const p2=await c2.newPage(),offErr=[];p2.on('pageerror',e=>offErr.push(String(e)));let nav=true,navError=null;
 try{await p2.goto(URL,{waitUntil:'domcontentloaded',timeout:60000});await waitReady(p2,60000);}catch(e){nav=false;navError=String(e);}
 out.checks.cold=await p2.evaluate(async()=>{async function f(u){try{const r=await fetch(u,{cache:'no-store'}),b=await r.arrayBuffer();return{ok:r.ok,status:r.status,bytes:b.byteLength}}catch(e){return{ok:false,error:String(e)}}}const s=await dbGet('settings','offline_completion').catch(()=>null);return{app:APP_VERSION,pub:PUBLIC_VERSION,pill:document.getElementById('version-pill-home')?.textContent||'',loading:getComputedStyle(document.getElementById('loading')).display!=='none',saved:s&&s.val,volume36:await f('./corpus/volume_36.json'),searchIndex:await f('./corpus/search_v2_index.json')};});
 out.checks.cold.nav=nav;out.checks.cold.navError=navError;out.checks.cold.pageErrors=offErr;await c2.close();

 out.pageErrors=pageErrors;out.consoleErrors=consoleErrors;
 const id=out.checks.identity,searchOk=out.checks.search.every(x=>!x.failed&&x.cards>0&&x.source===x.mode);
 const identityOk=id.app===EXPECT.app&&id.pub===EXPECT.pub&&id.swExpected===EXPECT.sw&&id.pill==='v139'&&id.version===EXPECT.app&&id.versionPub==='139'&&id.controller&&id.caches.some(x=>/shell-v2\.19\.139-R1B-ux-access-r12$/.test(x))&&id.caches.some(x=>/runtime-v2\.19\.139-R1B-ux-access-r12$/.test(x))&&!id.caches.some(x=>/shell-v2\.19\.(135|136|137|138)|runtime-v2\.19\.(135|136|137|138)/.test(x));
 const reader=out.checks.reader,readerOk=reader.opened===reader.firstId&&reader.readerTop<=2&&reader.favAfter&&reader.pressed==='true'&&reader.nextOk&&reader.next&&reader.next!==reader.old&&reader.restoredScreen==='screen-entries'&&reader.marker;
 const settingsOk=out.checks.settings.theme==='dark'&&out.checks.settings.text==='xlarge'&&out.checks.settingsReload.theme==='dark'&&out.checks.settingsReload.themeDb==='dark'&&out.checks.settingsReload.text==='xlarge';
 const assetsOk=Object.values(out.checks.assets).every(x=>x.ok&&x.bytes>0),layoutsOk=out.checks.layouts.every(x=>!x.overflow&&x.version==='v139');
 const offlineOk=out.checks.offline.ui==='READY'&&out.checks.offline.completed===204&&out.checks.offline.total===204&&out.checks.offline.failed===0&&out.checks.offline.saved&&out.checks.offline.saved.state==='READY';
 const cold=out.checks.cold,coldOk=cold.nav&&cold.app===EXPECT.app&&cold.pub==='139'&&cold.pill==='v139'&&!cold.loading&&cold.saved&&cold.saved.state==='READY'&&cold.volume36.ok&&cold.searchIndex.ok&&cold.pageErrors.length===0;
 out.assertions={servedExact:out.checks.served.exact,identity:identityOk,searchModes:searchOk,readerFavoriteNavigation:readerOk,espaceFavorite:out.checks.espace.storedBefore>=1&&out.checks.espace.count>=1,settingsPersistence:settingsOk,helpProvenance:out.checks.help.restored,assets:assetsOk,responsive:layoutsOk,backup:out.checks.backup.pass,offline:offlineOk,coldOffline:coldOk,noErrors:pageErrors.length===0&&consoleErrors.length===0};
 out.overall=Object.values(out.assertions).every(Boolean)?'PASS':'FAIL';
}
run().catch(e=>{out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}).finally(()=>{fs.writeFileSync('qa-ldc-v139-independent-reaudit-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({overall:out.overall,assertions:out.assertions,error:out.error},null,2));});
