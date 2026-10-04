const { chromium } = require('playwright');
const axeSource=require('axe-core').source;
const fs=require('fs');
const BASE='http://127.0.0.1:8096/lettres-v2.14-b1-csp-repair/';

function compact(r){
  return (r.violations||[]).filter(v=>v.id==='color-contrast').flatMap(v=>v.nodes.map(n=>({
    target:(n.target||[]).join(' > '),
    html:String(n.html||'').replace(/\s+/g,' ').slice(0,260),
    failureSummary:n.failureSummary
  })));
}
async function scan(p,label){
  await p.waitForTimeout(420);
  const r=await p.evaluate(async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
  return {label,nodes:compact(r)};
}
async function ready(p){
  await p.waitForFunction(()=>window.__LET_F_TEST && typeof switchPanel==='function' && document.querySelectorAll('.letter-item').length>0,{timeout:30000});
}
async function runScene(browser,viewport,theme){
  const c=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},colorScheme:theme});
  await c.addInitScript({content:axeSource});
  await c.addInitScript(t=>{localStorage.setItem('lp_theme',t);localStorage.setItem('lp_size','normal');},theme);
  const p=await c.newPage(); const errs=[];
  p.on('pageerror',e=>errs.push('PAGE '+String(e)));p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});
  await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000}); await ready(p); await p.waitForTimeout(500);
  const out={viewport:viewport.name,theme,scenes:[],errors:errs};
  for(const panel of ['p-home','p-list','p-search','p-notes','p-explore']){
    await p.evaluate(id=>switchPanel(id),panel);out.scenes.push(await scan(p,panel));
  }
  // Stable list + filter active/inactive state
  await p.evaluate(()=>switchPanel('p-list'));await p.waitForTimeout(420);
  out.scenes.push(await scan(p,'list-stable'));
  // Reader stable.
  const first=p.locator('.letter-item').first();
  if(await first.count()){await first.click();out.scenes.push(await scan(p,'reader'));}
  // Settings.
  await p.evaluate(()=>openTextBar());out.scenes.push(await scan(p,'settings'));
  // Transfer.
  await p.evaluate(()=>openDeviceTransferFromSettings());out.scenes.push(await scan(p,'transfer'));
  await p.evaluate(()=>{try{closeDeviceTransfer()}catch(e){};try{closeTextBar()}catch(e){}});await p.waitForTimeout(420);
  // Help.
  await p.evaluate(()=>openHelp('navigation',document.body));out.scenes.push(await scan(p,'help'));
  // Direct computed values for known suspects, stable state.
  await p.evaluate(()=>{try{closeHelp()}catch(e){}});await p.waitForTimeout(420);
  await p.evaluate(()=>openTextBar());await p.waitForTimeout(420);
  out.suspects=await p.evaluate(()=> {
    const ids=['settings-export-btn','snav-home','snav-list','snav-search','snav-notes','snav-explore','snav-settings','snav-help'];
    const ret={};
    for(const id of ids){const el=document.getElementById(id);if(el){const cs=getComputedStyle(el);ret[id]={display:cs.display,color:cs.color,background:cs.backgroundColor,opacity:cs.opacity,fontSize:cs.fontSize};}}
    for(const sel of ['.sidebar-bottom .build-meta','#home-scroll .build-meta','.chip','.chip.active','.li-dest','.topic-pill','.lrp-label']){
      const el=document.querySelector(sel);if(el){const cs=getComputedStyle(el);ret[sel]={display:cs.display,color:cs.color,background:cs.backgroundColor,opacity:cs.opacity,fontSize:cs.fontSize};}
    }
    return ret;
  });
  await c.close(); return out;
}
(async()=>{
 const b=await chromium.launch({headless:true});
 const out={candidateTree:'92530b7219fae7940be525b73b92d0a3782451ac',appVersion:'2.14',runs:[],status:'FAIL'};
 for(const theme of ['light','dark']){
   for(const vp of [{name:'phone',width:390,height:844},{name:'ipad',width:820,height:1180},{name:'desktop',width:1535,height:959}]){
      out.runs.push(await runScene(b,vp,theme));
   }
 }
 await b.close();out.status='PASS_EXECUTION';
 fs.writeFileSync('LETTRES_V2_14_STABLE_RENDERED_CONTRAST_AUDIT_2026-10-04.json',JSON.stringify(out,null,2));
 const agg=new Map();
 for(const run of out.runs) for(const sc of run.scenes) for(const n of sc.nodes){
   const m=String(n.failureSummary||'').match(/contrast of ([0-9.]+)/);const ratio=m?+m[1]:null;
   const key=n.target+'||'+n.html;
   if(!agg.has(key))agg.set(key,{target:n.target,html:n.html,ratios:[],contexts:[]});
   const x=agg.get(key);if(ratio!=null)x.ratios.push(ratio);x.contexts.push(run.viewport+'/'+run.theme+'/'+sc.label);
 }
 console.log(JSON.stringify([...agg.values()].map(x=>({target:x.target,html:x.html,min:x.ratios.length?Math.min(...x.ratios):null,max:x.ratios.length?Math.max(...x.ratios):null,contexts:[...new Set(x.contexts)]})).sort((a,b)=>(a.min??99)-(b.min??99)),null,2));
})().catch(e=>{console.error(e);process.exit(2)});