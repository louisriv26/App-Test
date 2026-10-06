const { chromium, webkit } = require('playwright');
const fs=require('fs');
const ROOT='marie-v50-test', BASE='http://127.0.0.1:8080/'+ROOT+'/';
const viewports=[
  {name:'screenshot',width:1215,height:751,tall:true},
  {name:'tablet',width:1024,height:768,tall:true},
  {name:'short-desktop',width:1200,height:600,tall:false},
  {name:'wide-threshold',width:768,height:600,tall:false}
];
async function ready(p){await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='50'&&State?.corpus?.length===37&&!document.getElementById('wide-loading').offsetParent,null,{timeout:30000}).catch(async()=>{await p.waitForFunction(()=>typeof APP_VERSION!=='undefined'&&APP_VERSION==='50'&&State?.corpus?.length===37,null,{timeout:30000})});}
async function setDay(p,day){await p.evaluate(day=>{const u=State.corpus.find(x=>x.day_number===day),d=App.getTodayData(u),c=document.getElementById('ws-today-card');if(!d)throw Error('missing day '+day);c.innerHTML='<div class="ws-today-label">✦ Pour aujourd\'hui — '+App.esc(d.ordinal)+'</div>'+(d.pratique?'<div class="ws-today-pratique">'+App.esc(d.pratique)+'</div>':'')+(d.oraison?'<div class="ws-today-oraison">'+App.esc(d.oraison)+'</div>':'');},day);}
async function measure(p){
 return p.evaluate(()=>{const q=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return{top:r.top,bottom:r.bottom,height:r.height,client:e.clientHeight,scroll:e.scrollHeight,flex:c.flex,max:c.maxHeight,font:c.fontSize,line:c.lineHeight}};const sb=q('#wide-sidebar'),c=q('#ws-today-card'),o=q('.ws-today-oraison');const vis=Math.max(0,Math.min(c.bottom,o.bottom)-Math.max(c.top,o.top));return{sb,c,o,free:sb.bottom-c.bottom,overflow:Math.max(0,c.scroll-c.client),fraction:o.height?vis/o.height:1};});
}
(async()=>{
 const evidence=[];
 for(const [engine,bt] of [['chromium',chromium],['webkit',webkit]]){
  const b=await bt.launch();
  for(const vp of viewports){
   for(const level of ['normal','large','xlarge']){
    const c=await b.newContext({viewport:{width:vp.width,height:vp.height},colorScheme:'light'});
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light')});
    const p=await c.newPage(),errs=[];p.on('pageerror',e=>errs.push(String(e)));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});await ready(p);await p.evaluate(()=>App.openDay(5));await p.evaluate(l=>App.applyTextSize(l,false),level);await p.waitForTimeout(60);
    const m=await measure(p);
    if(Math.abs(m.free)>1.5)throw new Error(engine+' '+vp.name+' '+level+' residual free space '+JSON.stringify(m));
    if(m.c.max!=='none'||m.c.flex!=='1 1 auto')throw new Error(engine+' '+vp.name+' '+level+' computed repair missing '+JSON.stringify(m.c));
    if(vp.tall && m.fraction<0.95)throw new Error(engine+' '+vp.name+' '+level+' Oraison insufficiently visible '+m.fraction);
    if(vp.name==='screenshot' && ['large','xlarge'].includes(level) && m.overflow>1)throw new Error(engine+' '+vp.name+' '+level+' screenshot regression still scrolls '+m.overflow);
    const bad=errs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));if(bad.length)throw new Error(engine+' '+vp.name+' '+level+' runtime errors '+JSON.stringify(bad));
    evidence.push({engine,viewport:vp.name,level,day:5,...m});
    await c.close();
   }
  }
  // Population challenge: all 31 days, all text sizes, screenshot geometry.
  for(const level of ['normal','large','xlarge']){
    const c=await b.newContext({viewport:{width:1215,height:751},colorScheme:'light'});
    await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','light')});
    const p=await c.newPage();await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});await ready(p);await p.evaluate(()=>App.openDay(5));await p.evaluate(l=>App.applyTextSize(l,false),level);
    for(let day=1;day<=31;day++){
      await setDay(p,day);await p.waitForTimeout(2);const m=await measure(p);
      if(Math.abs(m.free)>1.5)throw new Error(engine+' population '+level+' day '+day+' wasted space '+m.free);
      if(m.overflow>1 && m.free>1.5)throw new Error(engine+' population '+level+' day '+day+' overflow with free space');
      evidence.push({engine,viewport:'screenshot-population',level,day,...m});
    }
    await c.close();
  }
  await b.close();
 }
 fs.writeFileSync('MJV_v50_TODAY_CARD_GEOMETRY_EVIDENCE.json',JSON.stringify({status:'PASS',tree:'05f10479d5e9a5e476221cf7881fb5441cf5a909',evidence},null,2));
 console.log('MJV_V50_GEOMETRY_PASS',evidence.length);
})().catch(e=>{console.error(e);process.exit(2)});