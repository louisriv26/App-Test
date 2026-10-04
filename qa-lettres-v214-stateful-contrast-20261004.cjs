const { chromium }=require('playwright'); const axe=require('axe-core'); const fs=require('fs');
const BASE='http://127.0.0.1:8097/lettres-v2.14-b1-csp-repair/';
function rgb(s){const m=s.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);return m?[+m[1],+m[2],+m[3]]:null}
function lum(c){return c.map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0)}
function ratio(a,b){const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)}
async function axeScan(p,label){
 await p.waitForTimeout(450);
 const r=await p.evaluate(async src=>{eval(src);return await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}})},axe.source);
 return {label,nodes:r.violations.flatMap(v=>v.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary})))};
}
async function computed(p,sel){
 return await p.locator(sel).first().evaluate(el=>{const c=getComputedStyle(el);return {text:el.textContent.trim(),color:c.color,bg:c.backgroundColor,opacity:c.opacity,fontSize:c.fontSize,display:c.display}});
}
(async()=>{
 const b=await chromium.launch({headless:true}); const out=[];
 for(const theme of ['light','dark']){
   const c=await b.newContext({viewport:{width:820,height:1180},colorScheme:theme});
   await c.addInitScript(t=>{localStorage.setItem('lp_theme',t);localStorage.setItem('lp_size','normal');localStorage.setItem('lp_onboarded','1');},theme);
   const p=await c.newPage(); await p.goto(BASE,{waitUntil:'domcontentloaded'}); await p.waitForFunction(()=>window.__LET_F_TEST&&document.querySelectorAll('.letter-item').length);
   await p.waitForTimeout(500);
   const r={theme,scenes:[],direct:{}};
   // export primary
   await p.evaluate(()=>openTextBar('data')); await p.waitForTimeout(450);
   r.scenes.push(await axeScan(p,'settings-data'));
   r.direct.export=await computed(p,'#settings-export-btn');
   // direct ratio ignores transparency because button colors are opaque here
   {const a=rgb(r.direct.export.color),bb=rgb(r.direct.export.bg); r.direct.export.ratio=(a&&bb)?ratio(a,bb):null;}
   await p.evaluate(()=>closeTextBar(true));
   // mark letter 1 read via storage and reconcile UI
   await p.evaluate(()=>{localStorage.setItem('lp_read',JSON.stringify([1])); location.reload()});
   await p.waitForFunction(()=>window.__LET_F_TEST&&document.querySelectorAll('.letter-item').length); await p.waitForTimeout(500);
   await p.evaluate(()=>switchPanel('p-list')); await p.waitForTimeout(450);
   r.scenes.push(await axeScan(p,'list-read-state'));
   if(await p.locator('.li-read').count())r.direct.readTitle=await computed(p,'.li-read');
   // path done state: seed one path's first letter in lp_paths according to app's own runtime helper if possible
   const pathInfo=await p.evaluate(()=>({paths:(window.PATHS||[]).map(x=>({id:x.id,nums:(x.letters||x.letter_numbers||[])})).slice(0,3),keys:Object.keys(localStorage)}));
   // use app helpers: open first path then mark first displayed path letter's n as read via current path storage helper if available; fallback click/open close and mark as read
   await p.evaluate(()=>{switchPanel('p-explore');});
   await p.waitForTimeout(300);
   const firstPath=await p.locator('[data-path-id]').first().getAttribute('data-path-id');
   if(firstPath){
      await p.evaluate(id=>openPath(id),firstPath); await p.waitForTimeout(300);
      const n=Number(await p.locator('.path-letter-item').first().getAttribute('data-n'));
      // Paths derive done from readSet in current code? Ensure read set contains n and re-render.
      await p.evaluate(n=>{const arr=JSON.parse(localStorage.getItem('lp_read')||'[]');if(!arr.includes(n))arr.push(n);localStorage.setItem('lp_read',JSON.stringify(arr));location.reload()},n);
      await p.waitForFunction(()=>window.__LET_F_TEST&&document.querySelectorAll('.letter-item').length); await p.waitForTimeout(500);
      await p.evaluate(id=>{switchPanel('p-explore');openPath(id)},firstPath); await p.waitForTimeout(450);
      r.scenes.push(await axeScan(p,'path-done-state'));
      if(await p.locator('.path-letter-item.done').count()) {
        r.direct.pathDone=await computed(p,'.path-letter-item.done');
        r.direct.pathDoneTitle=await computed(p,'.path-letter-item.done .path-letter-title');
        r.direct.pathDoneMeta=await computed(p,'.path-letter-item.done .path-letter-meta');
      }
      await p.evaluate(()=>closePath(true));
   }
   // empty wide reader on fresh wide page after no current letter: reload and scan immediately.
   await p.evaluate(()=>{sessionStorage.clear();location.href=location.pathname+'?screen=list'});
   await p.waitForFunction(()=>window.__LET_F_TEST&&document.querySelectorAll('.letter-item').length); await p.waitForTimeout(500);
   r.scenes.push(await axeScan(p,'empty-wide-reader'));
   if(await p.locator('#reader-empty small').count()) r.direct.emptySmall=await computed(p,'#reader-empty small');
   out.push(r); await c.close();
 }
 await b.close(); fs.writeFileSync('LETTRES_V2_14_STATEFUL_CONTRAST_AUDIT_2026-10-04.json',JSON.stringify({candidateTree:'92530b7219fae7940be525b73b92d0a3782451ac',out},null,2));
 console.log(JSON.stringify(out,null,2));
})().catch(e=>{console.error(e);process.exit(2)})