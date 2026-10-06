const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const ROOT='ldc-v139-r12-search-v21a-recert';
const URL='http://127.0.0.1:8140/'+ROOT+'/';
const out={candidate:'LDC v139/R12 offline persistence diagnostic',generated_at:new Date().toISOString(),scenarios:{},overall:'UNKNOWN'};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function ready(p){
  await p.waitForFunction(()=>{const l=document.getElementById('loading'),v=document.getElementById('version-pill-home');return l&&getComputedStyle(l).display==='none'&&v&&v.textContent==='v139';},{timeout:90000});
  await p.waitForFunction(()=>navigator.serviceWorker.ready.then(()=>true),{timeout:30000});
  if(!await p.evaluate(()=>!!navigator.serviceWorker.controller)){await p.reload({waitUntil:'domcontentloaded',timeout:90000});await p.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',{timeout:90000});}
}

async function runScenario(name,withBackup){
  const profile=path.join(process.cwd(),'.qa-ldc-v139-offline-'+name);
  fs.rmSync(profile,{recursive:true,force:true});
  const c=await chromium.launchPersistentContext(profile,{headless:true,serviceWorkers:'allow',viewport:{width:1024,height:768}});
  const p=await c.newPage(),errors=[],consoleErrors=[];p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
  await p.goto(URL,{waitUntil:'domcontentloaded',timeout:90000});await ready(p);
  await sleep(1500);
  await p.evaluate(()=>{
    window.__offlineDiag={writes:[],poll:[],replaceCalls:[]};
    const origPut=dbPut;
    dbPut=async function(store,val){
      if(store==='settings'&&val&&val.key==='offline_completion')window.__offlineDiag.writes.push({at:Date.now(),state:val.val&&val.val.state,completed:val.val&&val.val.completed,stack:(new Error('offline_completion write')).stack});
      return origPut.apply(this,arguments);
    };
    const origReplace=dbReplaceUserDataAtomic;
    dbReplaceUserDataAtomic=async function(state){
      window.__offlineDiag.replaceCalls.push({at:Date.now(),phase:'start',offline:state&&state.settings&&state.settings.find(x=>x.key==='offline_completion')});
      try{return await origReplace.apply(this,arguments);}
      finally{window.__offlineDiag.replaceCalls.push({at:Date.now(),phase:'end'});}
    };
    window.__offlineDiagTimer=setInterval(async()=>{
      try{const r=await dbGet('settings','offline_completion');window.__offlineDiag.poll.push({at:Date.now(),saved:r&&(r.val||r.value)&&((r.val||r.value).state),ui:offlineUiState&&offlineUiState.state,completed:offlineUiState&&offlineUiState.completed});if(window.__offlineDiag.poll.length>500)window.__offlineDiag.poll.shift();}catch(_){}
    },100);
  });
  if(withBackup){
    await p.evaluate(async()=>{
      await setThemePreference('dark');
      const env=await collectUserDataEnvelope();
      await setThemePreference('light');
      const prepared=await prepareBackupEnvelopeForImport(env),bytes=new TextEncoder().encode(JSON.stringify(prepared.env)).length,validation=await validateBackupEnvelope(prepared.env,bytes);
      if(!validation.ok)throw new Error('backup validation failed '+validation.errors.join('; '));
      pendingBackupImport={kind:'legacy-json',env:prepared.env,validation,fileName:'diag.json',migrationSummary:prepared.summary};
      await confirmImportBackup();
    });
    await sleep(1000);
  }
  const pre=await p.evaluate(async()=>{const r=await dbGet('settings','offline_completion').catch(()=>null);return{saved:r&&(r.val||r.value),ui:offlineUiState};});
  await p.evaluate(()=>startOfflinePreparation());
  await p.waitForFunction(()=>typeof offlineUiState!=='undefined'&&['READY','ERROR','PARTIAL','CANCELLED'].includes(offlineUiState.state),{timeout:300000,polling:250});
  let readySeen=false;try{await p.waitForFunction(async()=>{const r=await dbGet('settings','offline_completion').catch(()=>null),v=r&&(r.val||r.value);return v&&v.state==='READY';},{timeout:10000,polling:50});readySeen=true;}catch(_){}
  await sleep(2500);
  const post=await p.evaluate(async()=>{clearInterval(window.__offlineDiagTimer);const r=await dbGet('settings','offline_completion').catch(()=>null);return{saved:r&&(r.val||r.value),ui:offlineUiState,diag:window.__offlineDiag};});
  await c.close();
  return{withBackup,pre,readySeen,post,errors:{page:errors,console:consoleErrors},pass:post.ui.state==='READY'&&post.saved&&post.saved.state==='READY'};
}

(async()=>{
 try{
   out.scenarios.no_backup=await runScenario('no-backup',false);
   out.scenarios.with_backup=await runScenario('with-backup',true);
   out.overall=(out.scenarios.no_backup.pass&&out.scenarios.with_backup.pass)?'PASS':'DIAGNOSTIC_REPRODUCED';
 }catch(e){out.overall='HARNESS_ERROR';out.error=String(e&&e.stack||e);}
 fs.writeFileSync('qa-ldc-v139-offline-diagnostic-results.json',JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({overall:out.overall,no_backup:{pass:out.scenarios.no_backup&&out.scenarios.no_backup.pass,readySeen:out.scenarios.no_backup&&out.scenarios.no_backup.readySeen,saved:out.scenarios.no_backup&&out.scenarios.no_backup.post&&out.scenarios.no_backup.post.saved&&out.scenarios.no_backup.post.saved.state,writes:out.scenarios.no_backup&&out.scenarios.no_backup.post&&out.scenarios.no_backup.post.diag.writes},with_backup:{pass:out.scenarios.with_backup&&out.scenarios.with_backup.pass,readySeen:out.scenarios.with_backup&&out.scenarios.with_backup.readySeen,saved:out.scenarios.with_backup&&out.scenarios.with_backup.post&&out.scenarios.with_backup.post.saved&&out.scenarios.with_backup.post.saved.state,writes:out.scenarios.with_backup&&out.scenarios.with_backup.post&&out.scenarios.with_backup.post.diag.writes,replaceCalls:out.scenarios.with_backup&&out.scenarios.with_backup.post&&out.scenarios.with_backup.post.diag.replaceCalls}},null,2));
})();
