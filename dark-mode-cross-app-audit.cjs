
const { chromium } = require('playwright');
const fs = require('fs');

const apps = [
  {name:'24H', url:'https://louisriv26.github.io/App-Test/24h-v119-b1-governed-r4/', scenes:[
    {name:'home'},
    {name:'help', js:"typeof showHelp==='function'&&showHelp()"},
    {name:'settings', js:"typeof showSettingsSheet==='function'&&showSettingsSheet()"}
  ]},
  {name:'LDC', url:'https://louisriv26.github.io/App-Test/ldc-v135-r8-governed-r7/', scenes:[
    {name:'home'},
    {name:'help', js:"typeof openHelp==='function'&&openHelp()"},
    {name:'theme-sheet', js:"typeof showThemeSheet==='function'&&showThemeSheet()"},
    {name:'size-sheet', js:"typeof showSizeSheet==='function'&&showSizeSheet()"}
  ]},
  {name:'Lettres', url:'https://louisriv26.github.io/App-Test/lettres-v2.9-b1-governed-r4/', scenes:[
    {name:'home'},
    {name:'help', js:"typeof openHelp==='function'&&openHelp()"}
  ]},
  {name:'Marie', url:'https://louisriv26.github.io/App-Test/marie-v46/', scenes:[{name:'home'}]},
  {name:'Hub', url:'https://louisriv26.github.io/Hub---Github/', scenes:[{name:'home'}]}
];

(async()=>{
 const browser=await chromium.launch({headless:true});
 const all=[];
 for(const app of apps){
  const context=await browser.newContext({colorScheme:'dark', viewport:{width:1366,height:1024}});
  const page=await context.newPage();
  const appOut={name:app.name,url:app.url,scenes:[],errors:[]};
  try{
    const resp=await page.goto(app.url,{waitUntil:'domcontentloaded',timeout:120000});
    appOut.http=resp&&resp.status();
    await page.waitForTimeout(3500);
    await page.evaluate(()=>{
      document.documentElement.setAttribute('data-theme','dark');
      try{localStorage.setItem('theme','dark')}catch(e){}
      try{localStorage.setItem('ldc-theme','dark')}catch(e){}
    });
    await page.waitForTimeout(300);
    for(const scene of app.scenes){
      try{
        if(scene.js){
          await page.evaluate(code=>{ try{ return (0,eval)(code); }catch(e){ return String(e); } },scene.js);
          await page.waitForTimeout(350);
        }
        const data=await page.evaluate(()=>{
          function parse(s){
            const m=String(s||'').match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\)/i);
            return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]}:null;
          }
          function chan(v){v/=255;return v<=0.04045?v/12.92:Math.pow((v+0.055)/1.055,2.4)}
          function l(c){return c?0.2126*chan(c.r)+0.7152*chan(c.g)+0.0722*chan(c.b):null}
          function cr(a,b){const x=l(a),y=l(b);if(x==null||y==null)return null;return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
          function bgFor(el){
            let n=el;
            while(n){
              const cs=getComputedStyle(n), c=parse(cs.backgroundColor);
              if(c && c.a>0.01) return c;
              n=n.parentElement;
            }
            return {r:255,g:255,b:255,a:1};
          }
          function ident(el){
            let s=el.tagName.toLowerCase();
            if(el.id)s+='#'+el.id;
            if(el.classList&&el.classList.length)s+='.'+[...el.classList].slice(0,3).join('.');
            return s;
          }
          const low=[];
          const visible=[...document.querySelectorAll('button,a,input,textarea,select,[role="button"],[role="tab"],[role="menuitem"],[role="option"],label,p,span,h1,h2,h3,h4,li')].filter(el=>{
            const cs=getComputedStyle(el),r=el.getBoundingClientRect();
            return cs.display!=='none'&&cs.visibility!=='hidden'&&+cs.opacity>0&&r.width>0&&r.height>0;
          });
          for(const el of visible){
            const cs=getComputedStyle(el), fg=parse(cs.color), bg=bgFor(el), rt=cr(fg,bg);
            if(!rt)continue;
            const text=(el.innerText||el.value||el.getAttribute('aria-label')||'').trim().replace(/\s+/g,' ').slice(0,120);
            const interactive=el.matches('button,a,input,textarea,select,[role="button"],[role="tab"],[role="menuitem"],[role="option"]');
            const iconOnly=interactive && !((el.innerText||el.value||'').trim()) && !!el.querySelector('svg,i');
            const fs=parseFloat(cs.fontSize)||16,fw=parseInt(cs.fontWeight)||400;
            const large=fs>=24 || (fs>=18.66&&fw>=700);
            const threshold=iconOnly?3:(large?3:4.5);
            if(rt<threshold){
              low.push({el:ident(el),text,ratio:+rt.toFixed(2),threshold,fg:cs.color,bg:'rgb('+bg.r+', '+bg.g+', '+bg.b+')',opacity:cs.opacity,fontSize:cs.fontSize,fontWeight:cs.fontWeight,interactive,iconOnly});
            }
          }
          const nativeSelects=[...document.querySelectorAll('select')].map(el=>{
            const cs=getComputedStyle(el), b=bgFor(el), f=parse(cs.color), r=cr(f,b);
            return {
              el:ident(el), aria:el.getAttribute('aria-label')||'', value:el.value,
              color:cs.color, background:cs.backgroundColor, colorScheme:cs.colorScheme,
              appearance:cs.appearance, webkitAppearance:cs.webkitAppearance,
              textContrast:r?+r.toFixed(2):null,
              nativeAppearance:!(cs.appearance==='none'||cs.webkitAppearance==='none'),
              darkBackground:l(b)<0.25
            };
          });
          const placeholders=[...document.querySelectorAll('input[placeholder],textarea[placeholder]')].map(el=>{
            const cs=getComputedStyle(el,'::placeholder'), b=bgFor(el), f=parse(cs.color), r=cr(f,b);
            return {el:ident(el),placeholder:el.getAttribute('placeholder')||'',color:cs.color,opacity:cs.opacity,contrast:r?+r.toFixed(2):null};
          });
          const veryLowInteractive=[...document.querySelectorAll('button,a,input,textarea,select')].filter(el=>{
            const cs=getComputedStyle(el),r=el.getBoundingClientRect();
            return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0;
          }).map(el=>{
            const cs=getComputedStyle(el), b=bgFor(el), f=parse(cs.color), rt=cr(f,b);
            return {el:ident(el),text:(el.innerText||el.value||el.getAttribute('aria-label')||'').trim().replace(/\s+/g,' ').slice(0,100),ratio:rt?+rt.toFixed(2):null,color:cs.color,background:cs.backgroundColor,border:cs.borderColor};
          }).filter(x=>x.ratio!==null&&x.ratio<3);
          return {htmlTheme:document.documentElement.getAttribute('data-theme'), low,nativeSelects,placeholders,veryLowInteractive};
        });
        appOut.scenes.push({name:scene.name,...data});
      }catch(e){appOut.errors.push(scene.name+': '+e.stack)}
    }
  }catch(e){appOut.errors.push('load: '+e.stack)}
  await context.close();
  all.push(appOut);
 }
 await browser.close();
 fs.writeFileSync('dark-mode-cross-app-audit.json',JSON.stringify({generatedAt:new Date().toISOString(),apps:all},null,2));
 for(const a of all){
   console.log('APP',a.name,'HTTP',a.http,'ERRORS',a.errors.length);
   for(const s of a.scenes){
     console.log(' SCENE',s.name,'LOW',s.low.length,'NATIVE_SELECTS',s.nativeSelects.length,'VERY_LOW_INTERACTIVE',s.veryLowInteractive.length);
     for(const x of s.low.slice(0,25)) console.log('  LOW',JSON.stringify(x));
     for(const x of s.nativeSelects) console.log('  SELECT',JSON.stringify(x));
     for(const x of s.veryLowInteractive.slice(0,15)) console.log('  VLOW',JSON.stringify(x));
   }
 }
})().catch(e=>{console.error(e);process.exit(1)});
