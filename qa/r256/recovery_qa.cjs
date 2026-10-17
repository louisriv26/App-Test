// R256 read-only QA harness against isolated localhost /App-Test scope.
// This simulates an old valid worker, broken R255 upgrade, and repaired R256 release.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium,webkit}=require('playwright');
const engine=process.env.R256_BROWSER==='webkit'?webkit:chromium;
const OLD='/tmp/ldc_r256_old',BAD='/tmp/ldc_r256_bad',GOOD=process.cwd();
let serving=OLD;const records=[];let problems=[];
function log(name,o={}){const item={name,stamp:new Date().toISOString(),...o};records.push(item);console.log("R256_RECOVERY "+JSON.stringify(item))}
function sleep(n){return new Promise(r=>setTimeout(r,n))}
const mime={'.html':'text/html','.json':'application/json','.js':'application/javascript','.mjs':'application/javascript','.css':'text/css','.woff2':'font/woff2','.woff':'font/woff','.png':'image/png','.ico':'image/x-icon'};
const server=http.createServer(async(req,res)=>{try{const u=new URL(req.url,'http://localhost');const p=decodeURIComponent(u.pathname).replace(/^\/+/,'').replace(/^App-Test\//,'')||'index.html';const file=path.join(serving,p);if(!file.startsWith(serving+'/'))throw Error('outside root');const data=await fs.promises.readFile(file);res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream','cache-control':'no-store'});res.end(data)}catch(e){res.writeHead(404);res.end('Not found: '+e.code)}});
async function probe(page){return page.evaluate(async()=>{
 const reg=await navigator.serviceWorker.getRegistration().catch(()=>null);
 let worker=navigator.serviceWorker.controller||reg?.active;
 let revision=null;
 if(worker)revision=await new Promise(resolve=>{const channel=new MessageChannel();const t=setTimeout(()=>resolve('TIMEOUT'),900);channel.port1.onmessage=e=>{clearTimeout(t);resolve(e.data?.version||null)};try{worker.postMessage({type:'LDC_GET_VERSION'},[channel.port2])}catch(e){clearTimeout(t);resolve('ERROR')}});
 return {version:typeof APP_VERSION!=='undefined'?APP_VERSION:null,bootStage:typeof bootStage!=='undefined'?bootStage:null,bootError:document.querySelector('#boot-error-code')?.textContent||null,normal:document.querySelector('#loading')?getComputedStyle(document.querySelector('#loading')).display==='none':null,revision,active:reg?.active?.state||null,waiting:reg?.waiting?.state||null,installing:reg?.installing?.state||null,offline:typeof offlineUiState!=='undefined'?{state:offlineUiState.state,completed:offlineUiState.completed,total:offlineUiState.total,failed:offlineUiState.failed?.length}:null}
});}
async function until(page,condition,ms){const deadline=Date.now()+ms;let last;while(Date.now()<deadline){last=await probe(page);if(condition(last))return last;await sleep(400)}return last;}
async function main(){
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port+'/App-Test/';
 const browser=await engine.launch({headless:true});const ctx=await browser.newContext({serviceWorkers:'allow'}),page=await ctx.newPage();
 page.on('pageerror',e=>problems.push(String(e).slice(0,200)));
 try{
  serving=OLD;
  await page.goto(origin,{waitUntil:'domcontentloaded',timeout:25000});
  let st=await until(page,s=>s.normal&&s.active==='activated',25000);log('baseline',{st});
  if(!st.normal||st.active!=='activated')throw Error('old baseline not ready');
  await page.evaluate(async()=>{await dbPut('settings',{key:'r256_synthetic_marker',val:{marker:'PRESERVED_R256'},ts:Date.now()})});
  log('marker_written',{value:await page.evaluate(async()=>await dbGet('settings','r256_synthetic_marker'))});
  serving=BAD;
  await page.evaluate(async()=>{const reg=await navigator.serviceWorker.getRegistration();await reg.update()});
  await sleep(1800);
  log('broken_patch_before_reload',{st:await probe(page)});
  await page.reload({waitUntil:'domcontentloaded',timeout:25000});
  st=await until(page,s=>!!s.bootError,15000);
  log('broken_r255_reproduction',{st});
  if(!st.bootError||!st.bootError.includes('SW_SYNC'))throw Error('broken v14245 boot SW_SYNC not reproduced');
  serving=GOOD;
  await page.locator('#boot-repair-btn').click({timeout:10000});
  st=await until(page,s=>s.version?.includes('142.46')&&s.normal&&s.active==='activated',35000);
  log('repaired_from_failure',{st});
  if(!st.normal||!st.version?.includes('142.46')||st.active!=='activated')throw Error('failed to restore v14246 from boot error');
  const marker=await page.evaluate(async()=>await dbGet('settings','r256_synthetic_marker'));
  log('marker_preserved',{marker});
  if(marker?.val?.marker!=='PRESERVED_R256')throw Error('synthetic IndexedDB state lost');
  const start=await page.evaluate(async()=>{await startOfflinePreparation();return offlineUiState.state});
  log('offline_preparation_started',{start});
  st=await until(page,s=>['READY','ERROR','PARTIAL'].includes(s.offline?.state),180000);
  log('offline_preparation_finished',{st});
  if(st.offline?.state!=='READY'||st.offline?.completed!==205)throw Error('offline cache failed '+JSON.stringify(st.offline));
  await ctx.setOffline(true);
  await page.reload({waitUntil:'domcontentloaded',timeout:20000});
  st=await until(page,s=>s.normal||!!s.bootError,20000);
  log('cold_offline_reopen',{st});
  if(!st.normal||!st.version?.includes('142.46'))throw Error('offline reopen failed');
  st=await until(page,s=>s.offline?.state==='READY'||s.offline?.state==='ERROR'||s.offline?.state==='PARTIAL',20000);
  log('cold_offline_preparation_verified',{st});
  if(st.offline?.state!=='READY'||st.offline?.completed!==205)throw Error('offline cache not restored as READY after restart');
  const m2=await page.evaluate(async()=>await dbGet('settings','r256_synthetic_marker'));
  log('offline_user_state',{marker:m2,errors:problems.slice(0,6)});
  if(m2?.val?.marker!=='PRESERVED_R256')throw Error('offline user marker missing');
 }finally{await ctx.close();await browser.close();await new Promise(r=>server.close(r))}
}
(async()=>{let ok=false;try{await main();ok=true}catch(e){log('FAILED',{error:String(e),stack:e.stack?.slice(0,800)})}fs.writeFileSync('r256-recovery-results.json',JSON.stringify({ok,records,problems},null,2));if(!ok)process.exitCode=1})()
