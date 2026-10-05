const { webkit } = require('playwright');
const fs=require('fs');
async function mutateRule(p){
 await p.evaluate(()=>{let t=null;for(const s of [...document.styleSheets]){let rs;try{rs=[...s.cssRules]}catch(_){continue}for(const q of rs)if(q.selectorText==='.ws-today-card'&&q.style.maxHeight){t=q;break}if(t)break}if(!t)throw Error('rule');t.style.flex='1 1 auto';t.style.maxHeight='none';t.style.paddingBottom='calc(12px + var(--safe-bottom))';});
}
async function setDay(p,day){
 await p.evaluate(day=>{const u=State.corpus.find(x=>x.day_number===day),d=App.getTodayData(u),c=document.getElementById('ws-today-card');if(!d)throw Error('missing day '+day);c.innerHTML='<div class="ws-today-label">✦ Pour aujourd\'hui — '+App.esc(d.ordinal)+'</div>'+(d.pratique?'<div class="ws-today-pratique">'+App.esc(d.pratique)+'</div>':'')+(d.oraison?'<div class="ws-today-oraison">'+App.esc(d.oraison)+'</div>':'');},day);
}
async function m(p){return p.evaluate(()=>{const c=document.getElementById('ws-today-card'),o=document.querySelector('.ws-today-oraison'),sb=document.getElementById('wide-sidebar');const C=c.getBoundingClientRect(),O=o.getBoundingClientRect(),S=sb.getBoundingClientRect();const vis=Math.max(0,Math.min(C.bottom,O.bottom)-Math.max(C.top,O.top));return{overflow:Math.max(0,c.scrollHeight-c.clientHeight),free:S.bottom-C.bottom,frac:O.height?vis/O.height:1,card:C.height,scroll:c.scrollHeight}})}
(async()=>{
 const out=[],b=await webkit.launch();
 for(const level of ['normal','large','xlarge'])for(const variant of ['current','flex_auto']){
  const c=await b.newContext({viewport:{width:1215,height:751}});
  await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light');});
  const p=await c.newPage();await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>typeof App!=='undefined'&&State.corpus?.length===37);await p.evaluate(()=>App.openDay(5));await p.evaluate(l=>App.applyTextSize(l,false),level);if(variant==='flex_auto')await mutateRule(p);
  for(let day=1;day<=31;day++){await setDay(p,day);await p.waitForTimeout(1);out.push({level,variant,day,...await m(p)});}
  const a=out.filter(x=>x.level===level&&x.variant===variant), clipped=a.filter(x=>x.overflow>1), ora=a.filter(x=>x.frac<.999);
  const worst=[...a].sort((x,y)=>y.overflow-x.overflow)[0];
  console.log('POP',JSON.stringify({level,variant,days:31,scrollClipped:clipped.length,oraisonNotFullyVisible:ora.length,worstDay:worst.day,worstOverflow:Math.round(worst.overflow),minOraisonFraction:Math.min(...a.map(x=>x.frac)),freeBelowDay5:Math.round(a.find(x=>x.day===5).free),day5Overflow:Math.round(a.find(x=>x.day===5).overflow),day5OraisonFraction:a.find(x=>x.day===5).frac}));
  await c.close();
 }
 await b.close();fs.writeFileSync('/tmp/MJV49_SIDEBAR_POPULATION_DIAGNOSTIC.json',JSON.stringify(out,null,2));
})();