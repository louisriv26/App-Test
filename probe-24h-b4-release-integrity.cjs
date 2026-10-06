const { chromium } = require('playwright');
const fs=require('fs'), crypto=require('crypto');
const dirs=['24h-v119-b1-governed-r4','24h-v120-b4-darkmode'];
const out={};
const b64=s=>crypto.createHash('sha256').update(s).digest('base64');
const hex=b=>crypto.createHash('sha256').update(b).digest('hex');
function constVal(src,name){
 const m=src.match(new RegExp("const\\s+"+name+"\\s*=\\s*['\\\"]([^'\\\"]+)['\\\"]"));
 return m?m[1]:null;
}
for(const d of dirs){
 const html=fs.readFileSync(d+'/index.html','utf8');
 const sw=fs.readFileSync(d+'/sw.js','utf8');
 const manifest=JSON.parse(fs.readFileSync(d+'/manifest.json','utf8'));
 const version=JSON.parse(fs.readFileSync(d+'/version.json','utf8'));
 const csp=(html.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
 const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
 const styles=[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(m=>m[1]);
 const scriptHashes=scripts.map(s=>'sha256-'+b64(s));
 const styleHashes=styles.map(s=>'sha256-'+b64(s));
 out[d]={
   shell_sha256:hex(fs.readFileSync(d+'/index.html')),
   index_luisa_equal:hex(fs.readFileSync(d+'/index.html'))===hex(fs.readFileSync(d+'/luisa_24_heures.html')),
   scriptHashes,
   scriptHashesAuthorized:scriptHashes.map(h=>csp.includes("'"+h+"'")),
   styleHashes,
   styleHashesAuthorized:styleHashes.map(h=>csp.includes("'"+h+"'")),
   shell:{APP_VERSION:constVal(html,'APP_VERSION'),BUILD_REVISION:constVal(html,'BUILD_REVISION'),APP_RELEASE_ID:constVal(html,'APP_RELEASE_ID')},
   sw:{APP_VERSION:constVal(sw,'APP_VERSION'),BUILD_REVISION:constVal(sw,'BUILD_REVISION'),RELEASE_ID:constVal(sw,'RELEASE_ID'),CACHE_NAME:constVal(sw,'CACHE_NAME'),CANONICAL_SHELL_SHA256:constVal(sw,'CANONICAL_SHELL_SHA256')},
   manifest:{version:manifest.version,build_revision:manifest.build_revision,release_id:manifest.release_id,release_sequence:manifest.release_sequence},
   version:{app_version:version.app_version,build_revision:version.build_revision,release_id:version.release_id,release_sequence:version.release_sequence,canonical_shell_sha256:version.canonical_shell_sha256,real_device_status:version.real_device_status,overall_release_status:version.overall_release_status}
 };
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const d of dirs){
   const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
   const page=await ctx.newPage();
   const consoleEvents=[],pageErrors=[],failed=[];
   page.on('console',m=>consoleEvents.push({type:m.type(),text:m.text()}));
   page.on('pageerror',e=>pageErrors.push(String(e)));
   page.on('requestfailed',r=>failed.push({url:r.url(),failure:r.failure()}));
   const res=await page.goto('http://127.0.0.1:8080/'+d+'/luisa_24_heures.html',{waitUntil:'domcontentloaded',timeout:30000});
   await page.waitForTimeout(1200);
   const runtime=await page.evaluate(async()=>{
     const v={
       showHome:typeof showHome,
       state:typeof state,
       contentText:(document.getElementById('content')?.innerText||'').slice(0,250),
       dataTheme:document.documentElement.getAttribute('data-theme'),
       swSupported:'serviceWorker' in navigator
     };
     if('serviceWorker'in navigator){
       try{
         const regs=await navigator.serviceWorker.getRegistrations();
         v.registrations=regs.map(r=>({scope:r.scope,installing:r.installing?.state,waiting:r.waiting?.state,active:r.active?.state,script:r.active?.scriptURL||r.installing?.scriptURL||r.waiting?.scriptURL}));
       }catch(e){v.swError=String(e)}
     }
     return v;
   });
   out[d].runtime={status:res?.status(),runtime,consoleEvents,pageErrors,failed};
   await ctx.close();
 }
 await browser.close();
 fs.mkdirSync('24h-b4-integrity-probe',{recursive:true});
 fs.writeFileSync('24h-b4-integrity-probe/REPORT.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out,null,2));
})().catch(e=>{console.error(e);process.exit(1)});