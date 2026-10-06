const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),crypto=require('crypto');
const RID='24h-v120-b6-20261003-adversarial-runtime-closure',SEQ=120000006;
function cp(a,b){fs.rmSync(b,{recursive:true,force:true});fs.mkdirSync(path.dirname(b),{recursive:true});fs.cpSync(a,b,{recursive:true})}
function sha(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')}
(async()=>{
 const out={events:[],states:[]};cp('24h-v119-b1-governed-r4','qa-upgrade/24h');
 const b=await chromium.launch({headless:true});const c=await b.newContext({viewport:{width:390,height:844}});
 c.on('serviceworker',w=>{out.events.push({type:'serviceworker',url:w.url(),time:Date.now()})});
 const p=await c.newPage();const cons=[];p.on('console',m=>cons.push({type:m.type(),text:m.text()}));p.on('pageerror',e=>cons.push({type:'pageerror',text:String(e)}));
 await p.goto('http://127.0.0.1:8091/24h/luisa_24_heures.html',{waitUntil:'domcontentloaded'});await p.waitForTimeout(1000);
 let reg=await p.evaluateHandle(async()=>await navigator.serviceWorker.ready);
 out.pre=await p.evaluate(async()=>{const r=await navigator.serviceWorker.ready;return {scope:r.scope,active:r.active&&{url:r.active.scriptURL,state:r.active.state},waiting:r.waiting&&{url:r.waiting.scriptURL,state:r.waiting.state},installing:r.installing&&{url:r.installing.scriptURL,state:r.installing.state}}});
 out.preSwFileSha=sha('qa-upgrade/24h/sw.js');
 cp('24h-v120-b6-adversarial','qa-upgrade/24h');
 out.postCopySwFileSha=sha('qa-upgrade/24h/sw.js');
 out.postCopyManifest=JSON.parse(fs.readFileSync('qa-upgrade/24h/manifest.json','utf8'));
 out.postCopyVersion=JSON.parse(fs.readFileSync('qa-upgrade/24h/version.json','utf8'));
 out.httpSw=await p.evaluate(async()=>{const r=await fetch('sw.js?diag='+Date.now(),{cache:'no-store'});return {status:r.status,text:await r.text()}});
 await p.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()});
 for(let i=0;i<80;i++){await p.waitForTimeout(250);const s=await p.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();return {active:r&&r.active&&{url:r.active.scriptURL,state:r.active.state},waiting:r&&r.waiting&&{url:r.waiting.scriptURL,state:r.waiting.state},installing:r&&r.installing&&{url:r.installing.scriptURL,state:r.installing.state}}});out.states.push({i,...s});if(s.waiting)break}
 out.console=cons;
 out.final=out.states[out.states.length-1];
 fs.writeFileSync('24h-b6-update-diagnostic.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify({pre:out.pre,preSwFileSha:out.preSwFileSha,postCopySwFileSha:out.postCopySwFileSha,httpSwStatus:out.httpSw.status,httpSwHasB6:out.httpSw.text.includes(RID),events:out.events,final:out.final,console:cons.slice(-20)},null,2));
 await c.close();await b.close();
 if(!out.final||!out.final.waiting)process.exit(2);
})().catch(e=>{console.error(e);process.exit(1)});