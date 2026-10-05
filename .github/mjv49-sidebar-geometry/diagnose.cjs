const { chromium, webkit } = require('playwright');
const fs=require('fs');
const cases=[
 {name:'screenshot_1215x751',width:1215,height:751},
 {name:'short_1200x600',width:1200,height:600},
 {name:'tablet_1024x768',width:1024,height:768},
 {name:'threshold_768x600',width:768,height:600}
];
function r(n){return typeof n==='number'?Math.round(n*100)/100:n}
async function mutateRule(p){
 await p.evaluate(()=>{
  let t=null;
  for(const s of [...document.styleSheets]){let rs;try{rs=[...s.cssRules]}catch(_){continue}
   for(const q of rs)if(q.selectorText==='.ws-today-card'&&q.style.maxHeight){t=q;break}
   if(t)break;
  }
  if(!t)throw Error('today rule not found');
  t.style.flex='1 1 auto';t.style.maxHeight='none';t.style.paddingBottom='calc(12px + var(--safe-bottom))';
 });
}
async function metrics(p){
 return p.evaluate(()=>{
  const g=s=>{const e=document.querySelector(s),x=e.getBoundingClientRect(),c=getComputedStyle(e);return{top:x.top,bottom:x.bottom,height:x.height,client:e.clientHeight,scroll:e.scrollHeight,font:c.fontSize,line:c.lineHeight,flex:c.flex,max:c.maxHeight}};
  const sb=g('#wide-sidebar'),c=g('#ws-today-card'),pr=g('.ws-today-pratique'),o=g('.ws-today-oraison'),n=g('#wide-reader-nav');
  const ov=Math.max(0,c.scroll-c.client),vis=Math.max(0,Math.min(c.bottom,o.bottom)-Math.max(c.top,o.top));
  return{sb,c,pr,o,n,free:sb.bottom-c.bottom,overflow:ov,oraisonFrac:o.height?vis/o.height:null,scrollNeeded:ov>1};
 });
}
(async()=>{
 const out=[];
 for(const [engine,bt] of [['chromium',chromium],['webkit',webkit]]){
  const b=await bt.launch();
  for(const vp of cases)for(const level of ['normal','large','xlarge'])for(const variant of ['current','flex_auto']){
   const c=await b.newContext({viewport:{width:vp.width,height:vp.height}});
   await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light');});
   const p=await c.newPage();await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});
   await p.waitForFunction(()=>typeof App!=='undefined'&&State.corpus?.length===37);
   await p.evaluate(()=>App.openDay(5));
   await p.evaluate(l=>App.applyTextSize(l,false),level);
   if(variant==='flex_auto')await mutateRule(p);
   await p.waitForTimeout(50);
   const m=await metrics(p);const clean=JSON.parse(JSON.stringify(m,(k,v)=>typeof v==='number'?r(v):v));
   out.push({engine,viewport:vp.name,level,variant,...clean});
   console.log('GEOM2',JSON.stringify({engine,viewport:vp.name,level,variant,free:clean.free,cardH:clean.c.height,client:clean.c.client,scroll:clean.c.scroll,overflow:clean.overflow,prFont:clean.pr.font,prLine:clean.pr.line,oFont:clean.o.font,oLine:clean.o.line,oH:clean.o.height,oFrac:clean.oraisonFrac,flex:clean.c.flex,max:clean.c.max,navTop:clean.n.top}));
   await c.close();
  }
  await b.close();
 }
 fs.writeFileSync('/tmp/MJV49_SIDEBAR_GEOMETRY_DIAGNOSTIC.json',JSON.stringify(out,null,2));
})();