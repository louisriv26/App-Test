const { chromium } = require('playwright');
const fs=require('fs'), crypto=require('crypto');
const paths=['24h-v119-b1-governed-r4','24h-v120-b4-darkmode'];
const out={};
function b64sha(s){return crypto.createHash('sha256').update(s).digest('base64');}
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const p of paths){
   const html=fs.readFileSync(p+'/luisa_24_heures.html','utf8');
   const scripts=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/gi)].map((m,i)=>({i,attrs:m[1],len:m[2].length,sha:b64sha(m[2])}));
   const csp=(html.match(/Content-Security-Policy" content="([^"]+)"/)||[])[1]||'';
   const consoleErrors=[], allConsole=[], pageErrors=[];
   const ctx=await browser.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
   const page=await ctx.newPage();
   page.on('console',m=>{allConsole.push(m.type()+': '+m.text()); if(m.type()==='error')consoleErrors.push(m.text())});
   page.on('pageerror',e=>pageErrors.push(String(e)));
   const res=await page.goto('http://127.0.0.1:8080/'+p+'/luisa_24_heures.html',{waitUntil:'domcontentloaded',timeout:120000});
   await page.waitForTimeout(1800);
   const runtime=await page.evaluate(()=>({
     readyState:document.readyState,
     title:document.title,
     bodyText:document.body.innerText.slice(0,500),
     dataTheme:document.documentElement.getAttribute('data-theme'),
     showHome:typeof showHome,
     state:typeof state,
     corpus:typeof CORPUS,
     appHtml:document.getElementById('app')?.innerHTML.slice(0,300)||null,
     scriptCount:document.scripts.length,
     styleClosure:!!document.getElementById('dark-mode-contrast-closure-v120')
   }));
   out[p]={status:res?.status(),scripts,cspScriptElem:(csp.match(/script-src-elem [^;]+/)||[])[0],scriptAuthorized:scripts.map(s=>csp.includes("'sha256-"+s.sha+"'")),runtime,consoleErrors,pageErrors,allConsole:allConsole.slice(-30)};
   await ctx.close();
 }
 await browser.close();
 fs.writeFileSync('24h-runtime-diagnostic.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out,null,2));
})().catch(e=>{console.error(e);process.exit(1)});