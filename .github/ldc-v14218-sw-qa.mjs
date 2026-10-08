import fs from 'node:fs';
import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const report={schema:'ldc-v14218-new-profile-service-worker-actual-browser-v1',status:'UNKNOWN',source_sha:process.env.GITHUB_SHA||null,
  checks:{},details:{},errors:[],real_hosted_origin:false,physical_ios:false,deployment_authority:'NONE'};
const port=8899,base='http://127.0.0.1:'+port;let browser,server;
const test=(name,condition,detail)=>{report.checks[name]=!!condition;if(detail!==undefined)report.details[name]=detail};
try{
  server=cp.spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:['ignore','ignore','inherit']});
  await new Promise(r=>setTimeout(r,900));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
  const context=await browser.newContext({serviceWorkers:'allow',viewport:{width:390,height:844}});
  const page=await context.newPage();page.setDefaultTimeout(90000);
  await page.addInitScript(()=>{
    window.__swBootstrapTrace=[];
    const c=navigator.serviceWorker;
    if(!c)return;
    const record=(phase,info)=>{window.__swBootstrapTrace.push({at:Date.now(),phase,info});};
    try{
      const original=c.register.bind(c);
      c.register=(...args)=>{
        record('register-called',args.map(x=>String(x)));
        return original(...args).then(reg=>{record('register-resolved',{scope:reg.scope,active:reg.active?.state||null,installing:reg.installing?.state||null});return reg;},
          error=>{record('register-rejected',String(error));throw error});
      };
      record('register-instrumented',true);
    }catch(e){record('register-instrumentation-failed',String(e));}
  });
  page.on('pageerror',e=>report.errors.push('PAGEERROR:'+String(e)));
  page.on('console',m=>{if(m.type()==='error')report.errors.push('CONSOLE:'+m.text())});
  page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP_'+r.status()+':'+r.url())});
  await page.goto(base+'/',{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:120000});
  const worker=await page.evaluate(async()=>{
    const startedReady=Date.now();
    const support=('serviceWorker' in navigator);
    if(!support)return {supported:false,active:false,scope:null,cacheName:null,requests:[],otherCaches:[],version:PUBLIC_VERSION,sw_expected:SW_CACHE_VERSION,offline_count:null,binding:null,app_manifest_version:null,controller:false,boot_stage:bootStage,origin:location.origin,secure_context:isSecureContext};
    let reg=await navigator.serviceWorker.getRegistration('./');
    while(!reg&&Date.now()-startedReady<30000){await new Promise(r=>setTimeout(r,250));reg=await navigator.serviceWorker.getRegistration('./');}
    if(!reg)return {supported:true,active:false,scope:null,cacheName:null,requests:[],otherCaches:[],version:PUBLIC_VERSION,sw_expected:SW_CACHE_VERSION,offline_count:null,binding:null,app_manifest_version:null,controller:!!navigator.serviceWorker.controller,boot_stage:bootStage,origin:location.origin,secure_context:isSecureContext,register_probe_error:null,registrations:(await navigator.serviceWorker.getRegistrations()).map(x=>({scope:x.scope,active:x.active?.state||null,waiting:x.waiting?.state||null,installing:x.installing?.state||null}))};
    const started=Date.now();
    while(!reg.active&&Date.now()-started<30000)await new Promise(r=>setTimeout(r,250));
    let cacheName=null,requests=[];
    const all=await caches.keys(),shell=all.find(x=>x.includes('shell-v2.19.142.18-R1B-reader-semantic-integration-wip'));
    const otherCaches=all.filter(x=>!x.includes('shell-v2.19.142.18-R1B-reader-semantic-integration-wip'));
    if(shell){cacheName=shell;const c=await caches.open(shell);requests=(await c.keys()).map(x=>new URL(x.url).pathname);}
    const m=await (await fetch('./offline_manifest.json',{cache:'reload'})).json();
    return {supported:true,active:!!reg.active,installing:reg.installing?.state||null,waiting:reg.waiting?.state||null,scope:reg.scope,cacheName,requests,otherCaches,version:PUBLIC_VERSION,
      sw_expected:SW_CACHE_VERSION,offline_count:m.asset_count,binding:m.content_binding_sha256,
      app_manifest_version:m.app_version,controller:!!navigator.serviceWorker.controller};
  });
  report.details.worker_install_snapshot={...worker,requests_count:worker.requests.length};
  report.details.sw_bootstrap_trace=await page.evaluate(()=>window.__swBootstrapTrace||null);
  const names=['/search_semantic_pack_guard_r4.js','/search_semantic_v3_core_r4.js','/search_semantic_hybrid_r6.js','/search_semantic_pack_registry_r6.js','/pls_v16/runtime_v1.mjs'];
  test('registered_worker_active',worker.active&&!!worker.scope,worker.scope);
  test('shell_14218_cache_created',!!worker.cacheName,worker.cacheName);
  test('correct_v14218_app_and_offline_manifest',worker.version==='142.18'&&String(worker.app_manifest_version||'').includes('142.18'),{version:worker.version,offline_version:worker.app_manifest_version});
  test('qualified_small_runtime_scripts_cached',names.every(n=>worker.requests.some(v=>v.endsWith(n))),{scripts:names,missing:names.filter(n=>!worker.requests.some(v=>v.endsWith(n)))});
  test('frozen_204_corpus_binding',worker.offline_count===204&&worker.binding==='1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384');
  test('no_heavy_model_in_shell',!worker.requests.some(u=>u.includes('/model/onnx')||u.endsWith('metadata.jsonl')||u.endsWith('vectors.i8')),{shell_entries:worker.requests.length});
  report.status=Object.values(report.checks).every(Boolean)&&report.errors.length===0?'PASS':'FAIL';
}catch(e){report.errors.push(String(e.stack||e));report.status='FAIL'}
finally{
  fs.writeFileSync('LDC_v142.18_SW_ACTUAL_BROWSER_QA.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  if(browser)await browser.close().catch(()=>{});
  if(server)server.kill('SIGTERM');
  if(report.status!=='PASS')process.exitCode=1;
}
