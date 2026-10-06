const { chromium } = require('playwright');
const fs=require('fs');
const BASE='http://127.0.0.1:8093/lettres-r9/';

function contrastJS(){
  function parseColor(s){
    const m=String(s||'').match(/rgba?\(([^)]+)\)/i); if(!m)return null;
    const p=m[1].replace(/\//g,' ').split(/[,\s]+/).filter(Boolean);
    const nums=p.map(x=>x.endsWith('%')?parseFloat(x)*2.55:parseFloat(x));
    return {r:nums[0],g:nums[1],b:nums[2],a:nums.length>3?nums[3]:1};
  }
  function comp(f,b){const a=f.a+b.a*(1-f.a);return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a};}
  function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
  function lum(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}
  function ratio(a,b){return (Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05)}
  function bgFor(el){
    let layers=[], n=el;
    while(n){const c=parseColor(getComputedStyle(n).backgroundColor);if(c&&c.a>0)layers.push(c);n=n.parentElement;}
    let bg={r:255,g:255,b:255,a:1};
    for(let i=layers.length-1;i>=0;i--)bg=comp(layers[i],bg);
    return bg;
  }
  function visible(el){const r=el.getBoundingClientRect(),cs=getComputedStyle(el);return r.width>1&&r.height>1&&cs.display!=='none'&&cs.visibility!=='hidden'&&+cs.opacity>0;}
  const roots=[...document.querySelectorAll('button,a,[role="button"],summary,input,select,textarea')].filter(visible);
  return roots.map((el,idx)=>{
    const samples=[];
    const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
    let n;
    while(n=walker.nextNode()){
      const text=(n.nodeValue||'').replace(/\s+/g,' ').trim();
      if(!text)continue;
      const pe=n.parentElement;if(!pe||!visible(pe))continue;
      const fg=parseColor(getComputedStyle(pe).color),bg=bgFor(pe);if(!fg)continue;
      samples.push({kind:'text',text:text.slice(0,80),tag:pe.tagName,cls:String(pe.className||''),color:getComputedStyle(pe).color,bg:getComputedStyle(pe).backgroundColor,ratio:ratio(comp(fg,bg),bg)});
    }
    for(const icon of el.querySelectorAll('i[class*="ti"]')){
      if(!visible(icon))continue;
      const fg=parseColor(getComputedStyle(icon).color),bg=bgFor(icon);if(!fg)continue;
      samples.push({kind:'icon',text:'',tag:'I',cls:String(icon.className||''),color:getComputedStyle(icon).color,bg:getComputedStyle(icon).backgroundColor,ratio:ratio(comp(fg,bg),bg)});
    }
    // Controls with value/placeholder but no child text.
    if(samples.length===0 && ['INPUT','SELECT','TEXTAREA'].includes(el.tagName)){
      const fg=parseColor(getComputedStyle(el).color),bg=bgFor(el);if(fg)samples.push({kind:'text',text:(el.value||el.placeholder||'').slice(0,80),tag:el.tagName,cls:String(el.className||''),color:getComputedStyle(el).color,bg:getComputedStyle(el).backgroundColor,ratio:ratio(comp(fg,bg),bg)});
    }
    const minText=samples.filter(x=>x.kind==='text').reduce((m,x)=>Math.min(m,x.ratio),99);
    const minIcon=samples.filter(x=>x.kind==='icon').reduce((m,x)=>Math.min(m,x.ratio),99);
    return {idx,tag:el.tagName,id:el.id||'',cls:String(el.className||''),label:(el.getAttribute('aria-label')||el.innerText||el.value||el.placeholder||'').trim().replace(/\s+/g,' ').slice(0,120),minText,minIcon,samples};
  });
}

(async()=>{
 const browser=await chromium.launch({headless:true});
 const out=[];
 for(const viewport of [{name:'wide',width:1535,height:959},{name:'mobile',width:390,height:844}]){
   for(const theme of ['light','dark']){
     const c=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},colorScheme:theme});
     const p=await c.newPage(); const errs=[];
     p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
     await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});
     await p.waitForFunction(()=>window.__LET_F_TEST&&typeof openTextBar==='function',{timeout:30000});
     await p.evaluate(t=>{try{setThemeFromSettings(t)}catch(e){document.documentElement.setAttribute('data-theme',t)}},theme);
     await p.waitForTimeout(300);
     async function scan(surface){
       const rows=await p.evaluate(contrastJS);
       out.push({viewport:viewport.name,theme,surface,rows,errors:[...errs]});
     }
     // main panels
     for(const panel of ['p-home','p-list','p-search','p-notes','p-explore']){
       await p.evaluate(id=>{if(typeof switchPanel==='function')switchPanel(id)},panel); await p.waitForTimeout(100); await scan(panel);
     }
     // settings
     await p.evaluate(()=>openTextBar()); await p.waitForTimeout(100); await scan('settings');
     // transfer modal
     await p.evaluate(()=>openDeviceTransferFromSettings()); await p.waitForTimeout(100); await scan('transfer');
     await p.evaluate(()=>{try{closeDeviceTransfer()}catch(e){};try{closeTextBar()}catch(e){}}); await p.waitForTimeout(100);
     // help
     await p.evaluate(()=>{try{openHelp('navigation',document.body)}catch(e){}}); await p.waitForTimeout(100); await scan('help');
     await c.close();
   }
 }
 await browser.close();
 const severe=[], low=[];
 for(const s of out) for(const r of s.rows){
   const item={viewport:s.viewport,theme:s.theme,surface:s.surface,...r};
   if(r.minText<2 || r.minIcon<1.5) severe.push(item); else if(r.minText<4.5 || r.minIcon<3) low.push(item);
 }
 const uniq=a=>{const m=new Map();for(const x of a){const k=[x.viewport,x.theme,x.surface,x.id,x.cls,x.label,x.minText.toFixed(3),x.minIcon.toFixed(3)].join('|');if(!m.has(k))m.set(k,x)}return [...m.values()]}
 const report={severe:uniq(severe),low:uniq(low),sceneCount:out.length,status:'DONE'};
 fs.writeFileSync('LETTRES_R9_CONTRAST_SWEEP_2026-10-04.json',JSON.stringify(report,null,2));
 console.log('SEVERE',JSON.stringify(report.severe,null,2));
 console.log('LOW',JSON.stringify(report.low,null,2));
})().catch(e=>{console.error(e);process.exit(2)});