const { chromium, webkit } = require('playwright');

const viewports = [
  {name:'screenshot_match', width:1024, height:633},
  {name:'threshold_768x600', width:768, height:600},
  {name:'ipad_1024x768', width:1024, height:768},
  {name:'wide_1199x600', width:1199, height:600},
  {name:'desktop_1200x800', width:1200, height:800}
];

const variants = {
  current: null,
  flex_auto: '.ws-today-card{flex:1 1 auto !important;max-height:none !important;padding-bottom:calc(12px + var(--safe-bottom)) !important;}',
  flex_zero: '.ws-today-card{flex:1 1 0 !important;max-height:none !important;padding-bottom:calc(12px + var(--safe-bottom)) !important;}'
};

function round(x){return Math.round(x*100)/100;}
async function measure(page){
  return await page.evaluate(() => {
    const box=(sel)=>{const e=document.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return {
      top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height,
      clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,overflowY:cs.overflowY,
      flexGrow:cs.flexGrow,flexShrink:cs.flexShrink,flexBasis:cs.flexBasis,
      minHeight:cs.minHeight,maxHeight:cs.maxHeight,display:cs.display
    }};
    const sidebar=box('#wide-sidebar'), card=box('#ws-today-card'), ora=box('.ws-today-oraison'), cal=box('.ws-cal-wrap'), head=box('.ws-header'), nav=box('#wide-reader-nav');
    let visOra=null;
    if(card&&ora){visOra=Math.max(0,Math.min(card.bottom,ora.bottom)-Math.max(card.top,ora.top));}
    return {
      viewport:{w:innerWidth,h:innerHeight,dpr:devicePixelRatio},
      wide:isWide(),
      sidebar, calendar:cal, progress:head, card, oraison:ora, readerNav:nav,
      freeBelow: sidebar&&card ? sidebar.bottom-card.bottom : null,
      cardOverflow: card ? card.scrollHeight-card.clientHeight : null,
      oraisonVisiblePx:visOra,
      oraisonVisibleFraction: ora&&ora.height ? visOra/ora.height : null,
      cardAtSidebarBottom: sidebar&&card ? Math.abs(sidebar.bottom-card.bottom)<1.5 : null,
      scrollNeeded: card ? card.scrollHeight>card.clientHeight+1 : null
    };
  });
}

(async()=>{
  const all=[];
  for(const [engine,bt] of [['chromium',chromium],['webkit',webkit]]){
    const browser=await bt.launch();
    for(const vp of viewports){
      for(const [variant,css] of Object.entries(variants)){
        const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
        await ctx.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light');});
        const p=await ctx.newPage();
        await p.goto('http://127.0.0.1:8142/',{waitUntil:'domcontentloaded'});
        await p.waitForFunction(()=>typeof App!=='undefined'&&typeof State!=='undefined'&&State.corpus?.length===37);
        await p.evaluate(()=>App.openDay(5));
        if(css) await p.addStyleTag({content:css});
        await p.waitForTimeout(50);
        const m=await measure(p);
        const clean=JSON.parse(JSON.stringify(m,(k,v)=>typeof v==='number'?round(v):v));
        all.push({engine,viewport:vp.name,variant,...clean});
        console.log('GEOM',JSON.stringify({engine,viewport:vp.name,variant,freeBelow:clean.freeBelow,cardH:clean.card?.height,clientH:clean.card?.clientHeight,scrollH:clean.card?.scrollHeight,overflow:clean.cardOverflow,oraH:clean.oraison?.height,oraVisible:clean.oraisonVisiblePx,oraFrac:clean.oraisonVisibleFraction,atBottom:clean.cardAtSidebarBottom,flex:[clean.card?.flexGrow,clean.card?.flexShrink,clean.card?.flexBasis],maxH:clean.card?.maxHeight,sidebarH:clean.sidebar?.height,navTop:clean.readerNav?.top},null,0));
        await ctx.close();
      }
    }
    await browser.close();
  }
  require('fs').writeFileSync('/tmp/MJV49_SIDEBAR_GEOMETRY_DIAGNOSTIC.json',JSON.stringify(all,null,2));
})();