const { chromium } = require('playwright');

const apps = [
  {app:'24H', url:'https://louisriv26.github.io/App-Test/24h-v119-b1-governed-r4/'},
  {app:'LDC', url:'https://louisriv26.github.io/App-Test/ldc-v135-r8-governed-r7/'},
  {app:'Lettres', url:'https://louisriv26.github.io/App-Test/lettres-v2.9-b1-governed-r4/'},
  {app:'Marie', url:'https://louisriv26.github.io/App-Test/marie-v46/'},
  {app:'Hub', url:'https://louisriv26.github.io/Hub---Github/'}
];

function lum(rgb){
  const m=rgb.match(/rgba?\(([^)]+)\)/); if(!m) return null;
  const a=m[1].split(',').map(x=>parseFloat(x.trim()));
  const c=a.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)});
  return .2126*c[0]+.7152*c[1]+.0722*c[2];
}
function ratio(a,b){const x=lum(a),y=lum(b); if(x==null||y==null)return null; return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}

(async()=>{
 const browser=await chromium.launch({headless:true});
 const out=[];
 for(const a of apps){
   const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:1024,height:768}});
   const p=await ctx.newPage();
   const errors=[];
   p.on('pageerror',e=>errors.push('pageerror:'+e.message));
   p.on('console',m=>{if(m.type()==='error') errors.push('console:'+m.text())});
   let status=null;
   try{
     const r=await p.goto(a.url,{waitUntil:'domcontentloaded',timeout:60000});
     status=r&&r.status();
     await p.waitForTimeout(5000);
     // Force dark only if the application exposes a data-theme model; system-dark remains active otherwise.
     await p.evaluate(()=>{ if(document.documentElement.hasAttribute('data-theme')) document.documentElement.setAttribute('data-theme','dark'); });
     await p.waitForTimeout(500);

     const data=await p.evaluate(()=>{
       function alpha(c){const m=c&&c.match(/rgba?\(([^)]+)\)/);if(!m)return 1;const z=m[1].split(',');return z.length>3?parseFloat(z[3]):1}
       function bg(el){
         let n=el;
         while(n&&n.nodeType===1){
           const c=getComputedStyle(n).backgroundColor;
           if(c && alpha(c)>0.02) return c;
           n=n.parentElement;
         }
         return getComputedStyle(document.documentElement).backgroundColor;
       }
       function visible(el){
         const s=getComputedStyle(el),r=el.getBoundingClientRect();
         return s.display!=='none'&&s.visibility!=='hidden'&&parseFloat(s.opacity||'1')>0.02&&r.width>0&&r.height>0;
       }
       const items=[];
       for(const el of document.querySelectorAll('body *')){
         if(!visible(el)) continue;
         const s=getComputedStyle(el), txt=(el.innerText||el.textContent||'').trim();
         const tag=el.tagName.toLowerCase();
         const hasOwnText=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
         const iconLike=tag==='i'||el.getAttribute('aria-hidden')==='true'||/icon|ti\s|chevron|arrow/i.test(el.className||'');
         if((hasOwnText&&txt)||iconLike){
           items.push({tag,id:el.id||'',cls:String(el.className||'').slice(0,120),text:txt.slice(0,100),color:s.color,bg:bg(el),fontSize:s.fontSize,fontWeight:s.fontWeight,opacity:s.opacity,iconLike});
         }
       }
       const controls=[...document.querySelectorAll('select,input,textarea,button')].map(el=>{
         const s=getComputedStyle(el);
         let ph=null; try{ph=getComputedStyle(el,'::placeholder').color}catch(e){}
         return {
           tag:el.tagName.toLowerCase(),type:el.type||'',id:el.id||'',cls:String(el.className||'').slice(0,140),
           color:s.color,bg:bg(el),borderColor:s.borderColor,appearance:s.appearance||s.webkitAppearance||'',
           colorScheme:s.colorScheme||'',accentColor:s.accentColor||'',placeholder:ph,
           visible:visible(el),aria:el.getAttribute('aria-label')||'',title:el.getAttribute('title')||''
         };
       });
       return {title:document.title,htmlTheme:document.documentElement.getAttribute('data-theme'),items,controls};
     });
     const low=[];
     for(const x of data.items){
       const rr=ratio(x.color,x.bg);
       if(rr!=null && rr<3.0) low.push({...x,ratio:+rr.toFixed(2)});
     }
     const controls=data.controls.map(x=>{
       const rr=ratio(x.color,x.bg);
       const br=ratio(x.borderColor,x.bg);
       const pr=x.placeholder?ratio(x.placeholder,x.bg):null;
       return {...x,textRatio:rr&&+rr.toFixed(2),borderRatio:br&&+br.toFixed(2),placeholderRatio:pr&&+pr.toFixed(2)};
     });
     out.push({app:a.app,url:a.url,status,title:data.title,theme:data.htmlTheme,lowContrast:low.slice(0,100),controls,errors:errors.slice(0,30)});
   }catch(e){out.push({app:a.app,url:a.url,status,error:String(e),errors});}
   await ctx.close();
 }
 console.log(JSON.stringify(out,null,2));
 await browser.close();
})();