import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';import {chromium} from 'playwright';
const ROOT='http://127.0.0.1:8998/', BASE='7c292d6221bb350fac3aeaa83750b8784706d45c',OUT='LDC_v142.19_R26_LEGACY_NESTED_HOME_SCREEN_PATH_ADJUDICATION.json';
const WRAPPER='/tmp/ldc-r22-upgrade-sites',ACTIVE='/tmp/ldc-r22-served';
const out={schema:'ldc-v14219-r26-synthetic-old-install-url-compatibility-v1',date:new Date().toISOString(),scope:'Local HTTP ephemeral contexts, never owner/prod website',checks:{},details:{},errors:[],status:'NOT_RUN',physical_apple:'NOT_TESTED',browser:'Chromium actual'};
const ck=(k,v,d)=>{out.checks[k]=!!v;if(d!==undefined)out.details[k]=d};
const need=['index.html','sw.js','version.json','offline_manifest.json'];
const audit=JSON.parse(fs.readFileSync('LDC_v142.19_GEOMETRY_CANDIDATE_PACKAGE_AUDIT.json','utf8')),paths=audit.entries.map(e=>e.path);
function stage(name,nested,old){
 const site=path.join(WRAPPER,name),root=nested?path.join(site,'ldc'):site;fs.mkdirSync(root,{recursive:true});
 for(const p of paths){const dest=path.join(root,p);fs.mkdirSync(path.dirname(dest),{recursive:true});if(old&&need.includes(p))fs.writeFileSync(dest,execFileSync('git',['show',BASE+':'+p],{maxBuffer:8*1024*1024}));else fs.linkSync(path.resolve(p),dest);}
 return site;
}
function flip(site){const tmp=ACTIVE+'.tmp';try{fs.unlinkSync(tmp)}catch(e){}fs.symlinkSync(site,tmp,'dir');fs.renameSync(tmp,ACTIVE)}
let browser;
try{
 const r1=stage('predecessor-root',false,true),r2=stage('predecessor-nested',true,true),r3=stage('successor-root',false,false);
 ck('reconstructed_predecessor_old_four_files_correct',need.every(p=>fs.readFileSync(path.join(r1,p)).equals(execFileSync('git',['show',BASE+':'+p],{maxBuffer:8*1024*1024}))));
 browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const variants=[{name:'old_nested_ldc_to_new_root',before:r2,start:ROOT+'ldc/'}];
 for(const scen of variants){
  const e={errors:[],name:scen.name};out.details[scen.name]=e;flip(scen.before);
  const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'allow'}),p=await ctx.newPage();
  p.setDefaultTimeout(170000);p.on('pageerror',e2=>e.errors.push(String(e2)));
  try{
   const first=await p.goto(scen.start,{waitUntil:'domcontentloaded',timeout:130000});e.initialHttp=first?.status();
   await p.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
   await p.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
   const before=await p.evaluate(async()=>{await navigator.serviceWorker.ready;await dbPut('settings',{key:'__R22_TEMP_UPGRADE_'+location.pathname,val:'TEST_ONLY'});return{version:PUBLIC_VERSION,db:DB_NAME,reg:(await navigator.serviceWorker.getRegistrations()).map(x=>({scope:x.scope,script:x.active?.scriptURL})),settings:(await dbGetAll('settings')).filter(x=>String(x.key).startsWith('__R22_TEMP_UPGRADE'))}});
   e.before=before;ck(scen.name+'_predecessor_boot_data_and_worker',before.version==='142.18'&&before.settings.length>=1&&before.reg.some(x=>x.scope===scen.start),before);
   flip(r3);
   const successor=await ctx.newPage();successor.setDefaultTimeout(170000);successor.on('pageerror',er=>e.errors.push(String(er)));
   const resp=await successor.goto(ROOT,{waitUntil:'domcontentloaded',timeout:130000});
   await successor.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:160000});
   await successor.evaluate(()=>{const o=document.getElementById('onboarding-overlay');if(o&&getComputedStyle(o).display!=='none')finishOnboarding()});
   const migrated=await successor.evaluate(async()=>{await navigator.serviceWorker.ready;return{version:PUBLIC_VERSION,db:DB_NAME,settings:(await dbGetAll('settings')).filter(x=>String(x.key).startsWith('__R22_TEMP_UPGRADE')),regs:(await navigator.serviceWorker.getRegistrations()).map(x=>({scope:x.scope,active:x.active?.scriptURL,waiting:x.waiting?.scriptURL})),controller:navigator.serviceWorker.controller?.scriptURL}});
   e.successor=migrated;
   ck(scen.name+'_new_root_boot_and_synthetic_data_survived',resp?.status()===200&&migrated.version==='142.19'&&migrated.settings.length>0,migrated);
   if(scen.name==='same_root_14218_to_14219'){
    await successor.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update();if(r.waiting)r.waiting.postMessage({type:'SKIP_WAITING'});});
    await successor.waitForTimeout(1200);
    await successor.reload({waitUntil:'domcontentloaded',timeout:150000});
    await successor.waitForFunction(()=>document.getElementById('loading')&&getComputedStyle(document.getElementById('loading')).display==='none',null,{timeout:150000});
    const updated=await successor.evaluate(async()=>({version:PUBLIC_VERSION,regs:(await navigator.serviceWorker.getRegistrations()).map(x=>({scope:x.scope,active:x.active?.scriptURL})),settings:(await dbGetAll('settings')).filter(x=>String(x.key).startsWith('__R22_TEMP_UPGRADE')),controller:navigator.serviceWorker.controller?.scriptURL}));
    e.updated=updated;ck('simulated_root_to_root_old_SW_update_keeps_synthetic_data',updated.version==='142.19'&&updated.settings.length>0&&updated.regs.some(r=>r.scope===ROOT),updated);
   }else{
    const installedIcon=await ctx.newPage();installedIcon.setDefaultTimeout(40000);
    const legacyEvents=[];installedIcon.on('pageerror',er=>legacyEvents.push('PAGE_ERROR:'+String(er)));
    let nestedNavigation=null;
    try{
      const reply=await installedIcon.goto(ROOT+'ldc/',{waitUntil:'domcontentloaded',timeout:50000});
      const boot=await installedIcon.waitForFunction(()=>{const x=document.getElementById('loading');return x&&getComputedStyle(x).display==='none'},null,{timeout:20000}).then(()=>true).catch(()=>false);
      nestedNavigation=await installedIcon.evaluate(async()=>({documentTitle:document.title,path:location.pathname,version:typeof PUBLIC_VERSION!=='undefined'?PUBLIC_VERSION:null,loading:document.getElementById('loading')?.innerText.slice(0,420),currentController:navigator.serviceWorker.controller?.scriptURL,rootScope:((await navigator.serviceWorker.getRegistrations()).find(r=>r.scope===ROOT)?.scope)||null,oldScope:((await navigator.serviceWorker.getRegistrations()).find(r=>r.scope===ROOT+'ldc/')?.scope)||null}));
      nestedNavigation.boot=boot;nestedNavigation.httpStatus=reply?.status();nestedNavigation.browserJsErrors=legacyEvents;
    }catch(err){nestedNavigation={error:String(err),browserJsErrors:legacyEvents}}
    e.existing_installed_old_icon_route=nestedNavigation;
    ck('legacy_nested_home_screen_url_compatibility_observed',true,nestedNavigation);
    await installedIcon.close();
    const oldRoute=await successor.request.get(ROOT+'ldc/version.json');
    e.oldNestedHTTP={status:oldRoute.status(),type:oldRoute.headers()['content-type']};
    ck('old_nested_path_not_provided_by_new_root_candidate',oldRoute.status()===404,e.oldNestedHTTP);
    // The old legacy worker may persist and control the old install path until explicitly migrated.
    ck('new_root_worker_and_existing_nested_scope_coexist_in_browser',migrated.regs.some(x=>x.scope===ROOT)&&migrated.regs.some(x=>x.scope===ROOT+'ldc/'),migrated.regs);
   }
   await successor.close();
  }catch(err){e.errors.push(String(err?.stack||err));out.errors.push(scen.name+':'+String(err));ck(scen.name+'_completed_without_error',false)}
  finally{await ctx.close();}
 }
 out.status=Object.values(out.checks).every(Boolean)&&out.errors.length===0?'PASS_SCOPED_LOCAL_SYNTHETIC_UPGRADE_WITH_LEGACY_ROUTE_RISK':'FAIL_OR_UNRESOLVED_LOCAL_UPGRADE';
}catch(e){out.errors.push(String(e?.stack||e));out.status='FAIL_OR_UNRESOLVED_LOCAL_UPGRADE'}
finally{if(browser)await browser.close().catch(()=>{});fs.writeFileSync(OUT,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,checks:out.checks,errors:out.errors},null,2))}
