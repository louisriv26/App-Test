const {chromium}=require('playwright');
function pc(s){const m=String(s||'').match(/rgba?\(([-.\d]+)[,\s]+([-.\d]+)[,\s]+([-.\d]+)(?:[,\s/]+([-.\d]+))?\)/i);return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]}:null}
function over(f,b){const a=f.a+b.a*(1-f.a);return{r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}}
function lin(v){v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}
function L(c){return .2126*lin(c.r)+.7152*lin(c.g)+.0722*lin(c.b)}
function ratio(a,b){const x=L(a),y=L(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
(async()=>{
 const browser=await chromium.launch({headless:true}); const out=[];
 for(const vp of [{name:'iphone',width:390,height:844},{name:'ipad',width:820,height:1180}]){
  const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height},colorScheme:'dark'});
  const p=await ctx.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(String(e)));
  const r=await p.goto('http://127.0.0.1:8080/marie-v47-b1-darkmode/',{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForTimeout(1800); await p.evaluate(()=>document.documentElement.setAttribute('data-theme','dark'));
  const x=await p.evaluate(()=>{
    function one(sel,bgSel){
      const e=document.querySelector(sel),b=document.querySelector(bgSel)||e;
      const ps=getComputedStyle(e,'::placeholder'),es=getComputedStyle(e),bs=getComputedStyle(b);
      return {sel,placeholder:ps.color,inputColor:es.color,inputBg:es.backgroundColor,containerBg:bs.backgroundColor,display:es.display};
    }
    return {search:one('#search-input','.search-row'),wideSearch:one('#wide-search-input','.search-row'),note:one('#note-textarea','#note-textarea')};
  });
  for(const [k,v] of Object.entries(x)){
    const fg=pc(v.placeholder); let bg=pc(v.inputBg); const cb=pc(v.containerBg);
    if(!bg||bg.a===0) bg=cb; else if(bg.a<1&&cb) bg=over(bg,cb);
    v.ratio=fg&&bg?+ratio(fg,bg).toFixed(3):null;
  }
  out.push({viewport:vp.name,http:r&&r.status(),errors,...x}); await ctx.close();
 }
 await browser.close();
 console.log(JSON.stringify(out,null,2));
 const bad=out.flatMap(o=>Object.entries({search:o.search,wideSearch:o.wideSearch,note:o.note}).filter(([k,v])=>v.ratio===null||v.ratio<4.5).map(([k,v])=>o.viewport+':'+k+':'+v.ratio));
 if(out.some(o=>o.http!==200||o.errors.length)||bad.length){console.error('MARIE_PLACEHOLDER_FAIL',bad);process.exit(2)}
 console.log('MARIE_PLACEHOLDER_PASS');
})().catch(e=>{console.error(e);process.exit(1)});