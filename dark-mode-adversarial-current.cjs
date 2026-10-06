
const { chromium } = require('playwright');
const fs = require('fs');
const apps=[
 {name:'24H',url:'http://127.0.0.1:8082/24h-v120-b3-darkmode/',scenes:[['home'],['help',"typeof showHelp==='function'&&showHelp()"],['settings',"typeof showSettingsSheet==='function'&&showSettingsSheet()"]]},
 {name:'LDC',url:'http://127.0.0.1:8082/ldc-v136-r9-darkmode/',scenes:[['home'],['help',"typeof openHelp==='function'&&openHelp()"],['theme',"typeof showThemeSheet==='function'&&showThemeSheet()"],['size',"typeof showSizeSheet==='function'&&showSizeSheet()"]]},
 {name:'Lettres',url:'http://127.0.0.1:8082/lettres-v2.12-b1-darkmode/',scenes:[['home'],['help',"typeof openHelp==='function'&&openHelp()"]]},
 {name:'Marie',url:'http://127.0.0.1:8082/marie-v47-b1-darkmode/',scenes:[['home']]},
 {name:'Hub',url:'https://louisriv26.github.io/Hub---Github/',scenes:[['home']]}
];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const out=[];
 for(const app of apps){
  const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:1366,height:1024}});
  const p=await ctx.newPage(); const ao={name:app.name,scenes:[],errors:[]};
  try{
   const res=await p.goto(app.url,{waitUntil:'domcontentloaded',timeout:120000}); ao.http=res&&res.status();
   await p.waitForTimeout(3500);
   await p.evaluate(()=>{document.documentElement.setAttribute('data-theme','dark')});
   for(const [name,js] of app.scenes){
    if(js){await p.evaluate(code=>{try{return (0,eval)(code)}catch(e){return String(e)}},js);await p.waitForTimeout(300)}
    const r=await p.evaluate(()=>{
      function pc(s){const m=String(s||'').match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\)/i);return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]}:null}
      function over(f,b){if(!f)return b;if(!b)b={r:255,g:255,b:255,a:1};const a=f.a+b.a*(1-f.a);if(a<=0)return{r:255,g:255,b:255,a:1};return{r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}}
      function bg(el){const chain=[];for(let n=el;n;n=n.parentElement)chain.push(n);let c={r:255,g:255,b:255,a:1};for(let i=chain.length-1;i>=0;i--){const x=pc(getComputedStyle(chain[i]).backgroundColor);if(x)c=over(x,c)}return c}
      function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
      function L(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}
      function ratio(a,b){if(!a||!b)return null;const x=L(a),y=L(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
      function id(el){let s=el.tagName.toLowerCase();if(el.id)s+='#'+el.id;if(el.classList&&el.classList.length)s+='.'+[...el.classList].slice(0,3).join('.');return s}
      function vis(el){const cs=getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&+cs.opacity>0&&r.width>0&&r.height>0}
      function directText(el){return [...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ').trim().replace(/\s+/g,' ')}
      const failures=[];
      const elems=[...document.querySelectorAll('body *')].filter(vis);
      for(const el of elems){
       const txt=directText(el);
       const isForm=el.matches('input,textarea,select');
       const val=isForm?(el.value||el.getAttribute('placeholder')||''):'';
       if(!txt&&!val)continue;
       // Ignore container text when all visible content is actually supplied by child elements.
       if(!txt && !isForm)continue;
       const cs=getComputedStyle(el),fg=pc(cs.color),ebg=bg(el),rr=ratio(fg,ebg);
       if(!rr)continue;
       const fs=parseFloat(cs.fontSize)||16,fw=parseInt(cs.fontWeight)||400,large=fs>=24||(fs>=18.66&&fw>=700);
       const th=large?3:4.5;
       if(rr<th)failures.push({el:id(el),text:(txt||val).slice(0,100),ratio:+rr.toFixed(2),threshold:th,fg:cs.color,bg:'rgb('+Math.round(ebg.r)+','+Math.round(ebg.g)+','+Math.round(ebg.b)+')',fontSize:cs.fontSize,fontWeight:cs.fontWeight});
      }
      const iconFailures=[];
      for(const el of elems.filter(x=>x.matches('svg,i,.ti,[aria-hidden="true"]'))){
        const cs=getComputedStyle(el),fg=pc(cs.color),ebg=bg(el),rr=ratio(fg,ebg);
        if(rr&&rr<3)iconFailures.push({el:id(el),ratio:+rr.toFixed(2),fg:cs.color,bg:'rgb('+Math.round(ebg.r)+','+Math.round(ebg.g)+','+Math.round(ebg.b)+')'});
      }
      const selects=[...document.querySelectorAll('select')].map(el=>{const cs=getComputedStyle(el),ebg=bg(el);return{el:id(el),aria:el.getAttribute('aria-label')||'',appearance:cs.appearance,webkitAppearance:cs.webkitAppearance,colorScheme:cs.colorScheme,color:cs.color,background:cs.backgroundColor,darkBg:L(ebg)<.25,native:cs.appearance!=='none'&&cs.webkitAppearance!=='none'}});
      const placeholders=[...document.querySelectorAll('input[placeholder],textarea[placeholder]')].filter(vis).map(el=>{const cs=getComputedStyle(el,'::placeholder'),ebg=bg(el),rr=ratio(pc(cs.color),ebg);return{el:id(el),text:el.getAttribute('placeholder'),ratio:rr?+rr.toFixed(2):null,color:cs.color,opacity:cs.opacity}}).filter(x=>x.ratio!==null&&x.ratio<4.5);
      return{theme:document.documentElement.getAttribute('data-theme'),failures,iconFailures,selects,placeholders};
    });
    ao.scenes.push({name,...r});
   }
  }catch(e){ao.errors.push(String(e&&e.stack||e))}
  await ctx.close(); out.push(ao);
 }
 await browser.close();
 fs.writeFileSync('dark-mode-adversarial-current-results.json',JSON.stringify({generatedAt:new Date().toISOString(),apps:out},null,2));
 for(const a of out){
  console.log('APP',a.name,'HTTP',a.http,'ERRORS',a.errors.length);
  for(const s of a.scenes){
   console.log(' SCENE',s.name,'TEXT_FAIL',s.failures.length,'ICON_FAIL',s.iconFailures.length,'SELECTS',s.selects.length,'PLACEHOLDER_FAIL',s.placeholders.length);
   for(const x of s.failures.slice(0,35))console.log('  TEXT',JSON.stringify(x));
   for(const x of s.iconFailures.slice(0,20))console.log('  ICON',JSON.stringify(x));
   for(const x of s.selects)console.log('  SELECT',JSON.stringify(x));
   for(const x of s.placeholders)console.log('  PLACEHOLDER',JSON.stringify(x));
  }
 }
})().catch(e=>{console.error(e);process.exit(1)});
