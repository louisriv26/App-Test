import fs from 'node:fs';
import cp from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import {chromium} from 'playwright-core';
const ports=[8963,8964], report={
 schema:'ldc-v14218-architectural-two-distinct-local-origins-v1',source_sha:process.env.GITHUB_SHA||null,
 status:'NOT_EXECUTED',checks:{},measurements:{},errors:[],
 hosted_e16:'OPEN',hosted_e19:'OPEN',real_production_origin_visited:false,
 deployment_authority:'NONE',scope:'two LOCAL ephemeral HTTP localhost:port origins in a single Chromium browser context'};
const check=(name,ok,val)=>{report.checks[name]=!!ok;if(val!==undefined)report.measurements[name]=val};
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ldc-e16-e19-local-sim-'));
let browser,servers=[];
try{
 fs.writeFileSync(path.join(tmp,'index.html'),'<!doctype html><title>Neutral test launcher</title><a href="/ldc/">LDC</a>');
 fs.mkdirSync(path.join(tmp,'24h'));
 fs.writeFileSync(path.join(tmp,'24h/index.html'),'<!doctype html><title>Sibling app sentinel</title><h1>Sibling 24H mock only</h1>');
 fs.symlinkSync(process.cwd(),path.join(tmp,'ldc'),'dir');
 for(const port of ports)servers.push(cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',tmp],{stdio:['ignore','ignore','inherit']}));
 await new Promise(r=>setTimeout(r,950));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'});
 const [a,b]=ports.map(p=>'http://127.0.0.1:'+p+'/');
 const ta=await ctx.newPage(),pb=await ctx.newPage();
 for(const [page,base] of [[ta,a],[pb,b]]){
   await page.goto(base+'ldc/',{waitUntil:'domcontentloaded',timeout:120000});
   await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:120000});
   await page.evaluate(()=>{if(document.getElementById('onboarding-overlay')&&getComputedStyle(document.getElementById('onboarding-overlay')).display!=='none')finishOnboarding()});
   await page.evaluate(async()=>{const r=await navigator.serviceWorker.ready; if(!r.active)throw Error('SW_NOT_ACTIVE');});
   await page.reload({waitUntil:'domcontentloaded',timeout:90000});
   await page.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:90000});
 }
 const read=async p=>p.evaluate(async()=>{
   const sw=await navigator.serviceWorker.getRegistrations();
   const keys=await caches.keys();
   return {origin:location.origin,path:location.pathname,controller:!!navigator.serviceWorker.controller,
     scope:sw.map(r=>r.scope), db_name:DB_NAME,cache_keys:keys};
 });
 const beforeA=await read(ta),beforeB=await read(pb);
 check('local_ports_are_distinct_origins',beforeA.origin!==beforeB.origin,{a:beforeA.origin,b:beforeB.origin});
 check('same_stable_local_DB_name_each_origin',beforeA.db_name==='ldc_user_v1'&&beforeA.db_name===beforeB.db_name);
 check('local_scoped_workers_only_control_ldc_folder',
   beforeA.controller&&beforeB.controller&&beforeA.scope.length===1&&beforeB.scope.length===1&&
   beforeA.scope[0]===a+'ldc/'&&beforeB.scope[0]===b+'ldc/',{a:beforeA,b:beforeB});
 const flag='E19_LOCAL_EPHEMERAL_T1';
 await ta.evaluate(async()=>{
   await dbPut('settings',{key:'E19_LOCAL_EPHEMERAL_T1',val:'TEST_ONLY_ALPHA',ts:Date.now()});
   localStorage.setItem('E19_LOCAL_EPHEMERAL_T1','TEST_ONLY_ALPHA');
   const c=await caches.open('E19_LOCAL_EPHEMERAL_ALPHA');await c.put('./marker-alpha',new Response('TEST_ONLY_ALPHA'));
 });
 const bBefore=await pb.evaluate(async()=>({
   db:await dbGet('settings','E19_LOCAL_EPHEMERAL_T1'),
   local:localStorage.getItem('E19_LOCAL_EPHEMERAL_T1'),
   caches:await caches.keys()
 }));
 check('test_origin_DB_write_invisible_to_production_simulation',bBefore.db==null,bBefore.db);
 check('test_origin_localStorage_invisible_to_second_origin',bBefore.local==null,bBefore.local);
 check('test_origin_CacheStorage_invisible_to_second_origin',!bBefore.caches.includes('E19_LOCAL_EPHEMERAL_ALPHA'),bBefore.caches);
 await pb.evaluate(async()=>{
   await dbPut('settings',{key:'E19_LOCAL_EPHEMERAL_T1',val:'TEST_ONLY_BETA',ts:Date.now()});
   localStorage.setItem('E19_LOCAL_EPHEMERAL_T1','TEST_ONLY_BETA');
   const c=await caches.open('E19_LOCAL_EPHEMERAL_BETA');await c.put('./marker-beta',new Response('TEST_ONLY_BETA'));
 });
 const aAfter=await ta.evaluate(async()=>({
   db:await dbGet('settings','E19_LOCAL_EPHEMERAL_T1'),
   local:localStorage.getItem('E19_LOCAL_EPHEMERAL_T1'),
   caches:await caches.keys()
 }));
 check('reverse_origin_DB_write_invisible_to_test_simulation',aAfter.db?.val==='TEST_ONLY_ALPHA',aAfter.db);
 check('reverse_origin_localStorage_invisible_to_test_simulation',aAfter.local==='TEST_ONLY_ALPHA',aAfter.local);
 check('reverse_origin_CacheStorage_invisible_to_test_simulation',!aAfter.caches.includes('E19_LOCAL_EPHEMERAL_BETA'),aAfter.caches);
 const sibling=await ctx.newPage();
 await sibling.goto(a+'24h/index.html',{waitUntil:'domcontentloaded'});
 const siblingState=await sibling.evaluate(()=>({controller:!!navigator.serviceWorker.controller,
   scopes:[],url:location.href,text:document.title}));
 check('local_ldc_worker_not_controlling_sibling_path',siblingState.controller===false,siblingState);
 const root=await ctx.newPage();
 await root.goto(a,{waitUntil:'domcontentloaded'});
 const rootState=await root.evaluate(()=>({controller:!!navigator.serviceWorker.controller,
   title:document.title,serviceWorkerMarkup:/serviceWorker\.register/.test(document.documentElement.innerHTML)}));
 check('neutral_local_root_has_no_worker_or_DB_logic',!rootState.controller&&!rootState.serviceWorkerMarkup,rootState);
 report.measurements.isolation_scope='ONLY local Chromium simulation; cannot close E16/E19 on GitHub-hosted same-origin environments';
 report.status=Object.values(report.checks).every(Boolean)?'PASS_LOCAL_SIMULATION_ONLY':'FAIL';
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{
 fs.writeFileSync('LDC_v142.18_LOCAL_E16_E19_SIMULATION_QA.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(browser)await browser.close().catch(()=>{});
 for(const p of servers)p.kill('SIGTERM');
 fs.rmSync(tmp,{recursive:true,force:true});
 if(report.status!=='PASS_LOCAL_SIMULATION_ONLY')process.exitCode=1;
}
