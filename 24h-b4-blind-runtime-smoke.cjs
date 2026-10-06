const { chromium } = require('playwright');
const fs=require('fs'), crypto=require('crypto');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const out={};
 for(const scheme of ['light','dark']){
  const ctx=await browser.newContext({colorScheme:scheme,viewport:{width:390,height:844}});
  const p=await ctx.newPage(); const consoleMsgs=[],pageErrors=[],requestFails=[];
  p.on('console',m=>consoleMsgs.push({type:m.type(),text:m.text()}));
  p.on('pageerror',e=>pageErrors.push(String(e)));
  p.on('requestfailed',r=>requestFails.push({url:r.url(),failure:r.failure()}));
  const r=await p.goto('http://127.0.0.1:8090/24h-v120-b4-darkmode/',{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForTimeout(1500);
  const info=await p.evaluate(()=>({
    title:document.title,
    theme:document.documentElement.getAttribute('data-theme'),
    body:(document.body.innerText||'').slice(0,500),
    functions:{
      showHome:typeof showHome,openHour:typeof openHour,showHelp:typeof showHelp,
      showSettingsSheet:typeof showSettingsSheet,showSearchView:typeof showSearchView
    },
    appChildren:document.querySelector('#app')?.children.length||0,
    loading:document.querySelector('[class*=loading]')?.textContent||null,
    buttons:document.querySelectorAll('button').length,
    swSupported:'serviceWorker' in navigator
  }));
  out[scheme]={http:r&&r.status(),consoleMsgs,pageErrors,requestFails,info};
  await ctx.close();
 }
 await browser.close();
 fs.writeFileSync('24h-b4-blind-runtime-smoke.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out,null,2));
 const bad=Object.values(out).some(x=>
   x.info.functions.showHome!=='function' || x.info.functions.openHour!=='function' ||
   x.consoleMsgs.some(m=>/content security policy|violates.*script-src|refused to execute/i.test(m.text))
 );
 if(bad) process.exit(2);
})().catch(e=>{console.error(e);process.exit(1)});