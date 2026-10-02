const { chromium } = require('playwright');

const apps=[
 {name:'24H',url:'https://louisriv26.github.io/App-Test/24h-v119-b1-governed-r4/'},
 {name:'LDC',url:'https://louisriv26.github.io/App-Test/ldc-v135-r8-governed-r7/'},
 {name:'Lettres',url:'https://louisriv26.github.io/App-Test/lettres-v2.9-b1-governed-r4/'},
 {name:'Marie',url:'https://louisriv26.github.io/App-Test/marie-v46/'},
 {name:'Hub',url:'https://louisriv26.github.io/Hub---Github/'}
];

(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const app of apps){
  const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:1366,height:1024}});
  const p=await ctx.newPage();
  const errors=[]; p.on('pageerror',e=>errors.push(e.message));
  const r=await p.goto(app.url,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForTimeout(3500);
  await p.evaluate(()=>document.documentElement.setAttribute('data-theme','dark'));
  await p.waitForTimeout(300);
  const out=await p.evaluate(()=>{
   function parse(s){
    const m=String(s||'').match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\)/i);
    return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]}:null;
   }
   function over(f,b){
    if(!f)return b; if(!b)b={r:255,g:255,b:255,a:1};
    const ba=(b.a===undefined?1:b.a), a=f.a+ba*(1-f.a);
    return {r:(f.r*f.a+b.r*ba*(1-f.a))/a,g:(f.g*f.a+b.g*ba*(1-f.a))/a,b:(f.b*f.a+b.b*ba*(1-f.a))/a,a};
   }
   function backdrop(el,includeSelf=true){
    const chain=[]; let n=includeSelf?el:el.parentElement;
    while(n&&n.nodeType===1){chain.push(n);n=n.parentElement}
    let c={r:255,g:255,b:255,a:1};
    for(const x of chain.reverse()){
      const bg=parse(getComputedStyle(x).backgroundColor);
      if(bg&&bg.a>0)c=over(bg,c);
    }
    return c;
   }
   function fg(el,bg){
    const c=parse(getComputedStyle(el).color); return c?over(c,bg):null;
   }
   function ch(v){v/=255;return v<=0.04045?v/12.92:Math.pow((v+0.055)/1.055,2.4)}
   function lum(c){return c?0.2126*ch(c.r)+0.7152*ch(c.g)+0.0722*ch(c.b):null}
   function cr(a,b){const x=lum(a),y=lum(b);if(x==null||y==null)return null;return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
   function vis(el){const cs=getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&+cs.opacity>0.01&&r.width>0&&r.height>0}
   function id(el){return el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(el.classList&&el.classList.length?'.'+[...el.classList].slice(0,4).join('.'):'')}
   function ownText(el){return [...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ').trim().replace(/\s+/g,' ').slice(0,120)}
   const lowText=[];
   for(const el of [...document.querySelectorAll('body *')].filter(vis)){
     const text=ownText(el); if(!text)continue;
     const cs=getComputedStyle(el),bg=backdrop(el,true),f=fg(el,bg),ratio=cr(f,bg);
     const fs=parseFloat(cs.fontSize)||16,fw=parseInt(cs.fontWeight)||400,large=fs>=24||(fs>=18.66&&fw>=700),th=large?3:4.5;
     if(ratio!=null&&ratio<th)lowText.push({el:id(el),text,ratio:+ratio.toFixed(2),threshold:th,color:cs.color,background:cs.backgroundColor});
   }
   const component=[];
   for(const el of [...document.querySelectorAll('button,[role="button"],[role="tab"],select,input')].filter(vis)){
     const cs=getComputedStyle(el),raw=parse(cs.backgroundColor);
     if(!raw||raw.a<=0.01)continue;
     const parent=backdrop(el,false),comp=over(raw,parent),ratio=cr(comp,parent);
     const rr=el.getBoundingClientRect();
     if(ratio!=null&&ratio<3&&rr.width>=4&&rr.height>=4)component.push({el:id(el),ratio:+ratio.toFixed(2),background:cs.backgroundColor,parentBg:'rgb('+parent.r.toFixed(0)+','+parent.g.toFixed(0)+','+parent.b.toFixed(0)+')',w:+rr.width.toFixed(0),h:+rr.height.toFixed(0)});
   }
   const selects=[...document.querySelectorAll('select')].map(el=>{
     const cs=getComputedStyle(el),bg=backdrop(el,true),f=fg(el,bg),ratio=cr(f,bg);
     return {el:id(el),visible:vis(el),appearance:cs.appearance,webkitAppearance:cs.webkitAppearance,colorScheme:cs.colorScheme,textContrast:ratio&&+ratio.toFixed(2),darkBg:lum(bg)<.25};
   });
   const known={};
   const sels=[
    '.onboarding-primary','.resume-panel-btn.primary','.sf-btn.active','.mark-btn','.update-banner','.note-save-btn','.theme-pref-btn.active',
    '.search-mode-badge','.rc-tag','.hsi-gold','.help-chip.light','.help-tip','.autour-card-tag','.rc-btn','.btn-primary',
    '#help-topic-select','#search-sort','.help-dot','.help-dot.active','.path-step.done','.search-term-flash',
    '.backup-btn.primary','.wt-nav-btn.active'
   ];
   for(const s of sels){
    let el=null; try{el=document.querySelector(s)}catch(e){}
    if(!el)continue;
    const cs=getComputedStyle(el),bg=backdrop(el,true),f=fg(el,bg),rr=cr(f,bg);
    known[s]={visible:vis(el),textContrast:rr&&+rr.toFixed(2),color:cs.color,background:cs.backgroundColor};
   }
   return {lowText,component,selects,known};
  });
  console.log('APP '+app.name+' HTTP '+(r&&r.status())+' ERRORS '+errors.length);
  console.log(JSON.stringify(out));
  await ctx.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});