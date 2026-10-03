const { chromium } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:390,height:844}});
 const page=await ctx.newPage();
 await page.goto('http://127.0.0.1:8080/marie-v47-b1-darkmode/',{waitUntil:'domcontentloaded',timeout:120000});
 await page.waitForTimeout(1500);
 await page.evaluate(()=>document.documentElement.setAttribute('data-theme','dark'));
 const out=await page.evaluate(()=>{
  const pc=s=>{const m=String(s).match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[,\s/]+/).filter(Boolean).map(Number);return{r:a[0],g:a[1],b:a[2],a:a[3]===undefined?1:a[3]}};
  const over=(f,b)=>{const a=f.a+b.a*(1-f.a);return{r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}};
  const bg=el=>{const chain=[];for(let n=el;n;n=n.parentElement)chain.push(n);let c={r:255,g:255,b:255,a:1};for(let i=chain.length-1;i>=0;i--){const x=pc(getComputedStyle(chain[i]).backgroundColor);if(x)c=over(x,c)}return c};
  const lin=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};
  const L=c=>.2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b);
  const ratio=(a,b)=>{const x=L(a),y=L(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
  const rows=[];
  for(const sel of ['#search-input','#wide-search-input','#note-textarea']){
   const el=document.querySelector(sel);if(!el){rows.push({sel,missing:true});continue}
   const cs=getComputedStyle(el),ps=getComputedStyle(el,'::placeholder'),b=bg(el),p=pc(ps.color),base=pc(cs.color);
   rows.push({sel,elementColor:cs.color,placeholderColor:ps.color,placeholderOpacity:ps.opacity,background:{r:Math.round(b.r),g:Math.round(b.g),b:Math.round(b.b)},ratio:p?+ratio(p,b).toFixed(3):null,baseRatio:base?+ratio(base,b).toFixed(3):null});
  }
  const rules=[];for(const ss of [...document.styleSheets]){let rs;try{rs=ss.cssRules}catch(e){continue}for(const r of [...rs])if(r.cssText&&r.cssText.includes('::placeholder'))rules.push(r.cssText)}
  return{theme:document.documentElement.getAttribute('data-theme'),rows,rules};
 });
 console.log(JSON.stringify(out,null,2));
 if(out.rows.some(r=>r.ratio!==null&&r.ratio<4.5)){console.error('MARIE_PLACEHOLDER_FAIL');process.exitCode=2}else console.log('MARIE_PLACEHOLDER_PASS');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});