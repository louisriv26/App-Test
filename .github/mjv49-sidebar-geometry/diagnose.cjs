const { chromium, webkit } = require('playwright');
const fs=require('fs');

const viewports=[
 {name:'screenshot_1215x751',width:1215,height:751},
 {name:'desktop_1200x750',width:1200,height:750},
 {name:'tablet_1199x750',width:1199,height:750},
 {name:'ipad_1024x768',width:1024,height:768},
 {name:'short_1200x600',width:1200,height:600},
 {name:'threshold_768x600',width:768,height:600}
];

function round(x){return typeof x==='number'?Math.round(x*100)/100:x;}
async function setVariant(p,variant){
 await p.evaluate((variant)=>{
   let target=null;
   for(const sheet of [...document.styleSheets]){
     let rules; try{rules=[...sheet.cssRules]}catch(_){continue}
     for(const rule of rules){
       if(rule.selectorText==='.ws-today-card' && rule.style.maxHeight){target=rule;break}
     }
     if(target) break;
   }
   if(!target) throw new Error('target .ws-today-card rule not found');
   if(variant==='flex_auto'){
     target.style.flex='1 1 auto'; target.style.maxHeight='none'; target.style.paddingBottom='calc(12px + var(--safe-bottom))';
   } else if(variant==='flex_zero'){
     target.style.flex='1 1 0'; target.style.maxHeight='none'; target.style.paddingBottom='calc(12px + var(--safe-bottom))';
   }
 },variant);
}
async function setTodayDay(p,day){
 await p.evaluate((day)=>{
   const u=State.dayMap[day], data=App.getTodayData(u), c=document.getElementById('ws-today-card');
   c.innerHTML='<div class="ws-today-label">✦ Pour aujourd\'hui — '+App.esc(data.ordinal)+'</div>'+
     (data.pratique?'<div class="ws-today-pratique">'+App.esc(data.pratique)+'</div>':'')+
     (data.oraison?'<div class="ws-today-oraison">'+App.esc(data.oraison)+'</div>':'');
 },day);
}
async function measure(p){
 return p.evaluate(()=>{
  const box=(sel)=>{const e=document.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect(),cs=getComputedStyle(e);return {top:r.top,bottom:r.bottom,height:r.height,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,overflowY:cs.overflowY,flexGrow:cs.flexGrow,flexShrink:cs.flexShrink,flexBasis:cs.flexBasis,minHeight:cs.minHeight,maxHeight:cs.maxHeight}};
  const sidebar=box('#wide-sidebar'),card=box('#ws-today-card'),ora=box('.ws-today-oraison'),nav=box('#wide-reader-nav');
  const vis=card&&ora?Math.max(0,Math.min(card.bottom,ora.bottom)-Math.max(card.top,ora.top)):null;
  return {viewport:{w:innerWidth,h:innerHeight},sidebar,card,oraison:ora,readerNav:nav,
    freeBelow:sidebar&&card?sidebar.bottom-card.bottom:null,
    overflow:card?card.scrollHeight-card.clientHeight:null,
    scrollNeeded:card?card.scrollHeight>card.clientHeight+1:null,
    oraisonVisiblePx:vis,
    oraisonFraction:ora&&ora.height?vis/ora.height:null};
 });
}

(async()=>{
 const all=[];
 for(const [engine,bt] of [['chromium',chromium],['webkit',webkit]]){
  const browser=await bt.launch();
  for(const vp of viewports){
   for(const variant of ['current','flex_auto','flex_zero']){
    const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
    await ctx.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light');});
    const p=await ctx.newPage();
    await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});
    await p.waitForFunction(()=>typeof App!=='undefined'&&State.corpus?.length===37);
    await p.evaluate(()=>App.openDay(5));
    if(variant!=='current') await setVariant(p,variant);
    await setTodayDay(p,5); await p.waitForTimeout(20);
    const m=await measure(p);
    const clean=JSON.parse(JSON.stringify(m,(k,v)=>typeof v==='number'?round(v):v));
    all.push({engine,viewport:vp.name,variant,day:5,...clean});
    console.log('GEOM',JSON.stringify({engine,viewport:vp.name,variant,day:5,freeBelow:clean.freeBelow,cardH:clean.card?.height,clientH:clean.card?.clientHeight,scrollH:clean.card?.scrollHeight,overflow:clean.overflow,oraH:clean.oraison?.height,oraVisible:clean.oraisonVisiblePx,oraFrac:clean.oraisonFraction,flex:[clean.card?.flexGrow,clean.card?.flexShrink,clean.card?.flexBasis],maxH:clean.card?.maxHeight,sidebarH:clean.sidebar?.height,navTop:clean.readerNav?.top}));
    if(vp.name==='screenshot_1215x751'){
      for(const day of Array.from({length:31},(_,i)=>i+1)){
        await setTodayDay(p,day); await p.waitForTimeout(1);
        const d=await measure(p);
        all.push({engine,viewport:vp.name,variant,day,...d});
      }
    }
    await ctx.close();
   }
  }
  await browser.close();
 }
 fs.writeFileSync('/tmp/MJV49_SIDEBAR_GEOMETRY_DIAGNOSTIC.json',JSON.stringify(all,null,2));
})();