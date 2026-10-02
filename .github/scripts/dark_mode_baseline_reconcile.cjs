const { chromium } = require('playwright');
const fs = require('fs');
const crypto = require('crypto');

function sha256(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')}
function parse(s){const m=String(s||'').match(/[0-9.]+/g);return (!m||m.length<3)?null:{r:+m[0],g:+m[1],b:+m[2],a:m[3]===undefined?1:+m[3]}}
function lum(c){const f=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)}
function cr(a,b){const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
function fileFacts(p, terms){
  const s=fs.readFileSync(p,'utf8');
  const out={path:p,bytes:Buffer.byteLength(s),sha256:sha256(p),terms:{}};
  for(const t of terms){const i=s.indexOf(t);out.terms[t]=i<0?null:s.slice(Math.max(0,i-220),Math.min(s.length,i+t.length+320));}
  return out;
}
async function pageProbe(browser,name,url,after){
  const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:1366,height:1024}});
  const p=await ctx.newPage(); const errors=[]; p.on('pageerror',e=>errors.push(e.message));
  const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
  await p.waitForTimeout(2500);
  await p.evaluate(()=>document.documentElement.setAttribute('data-theme','dark'));
  await p.waitForTimeout(200);
  const helpers = async () => {};
  async function inject(id,tag,cls,text,attrs={}){
    await p.evaluate(({id,tag,cls,text,attrs})=>{
      document.getElementById(id)?.remove();
      const el=document.createElement(tag);el.id=id;el.className=cls;el.textContent=text;
      for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);
      el.style.position='fixed';el.style.left='10px';el.style.top='10px';el.style.zIndex='2147483647';document.body.appendChild(el);
    },{id,tag,cls,text,attrs});
  }
  async function measure(sel,pseudo=null){
    return await p.evaluate(({sel,pseudo})=>{
      const el=document.querySelector(sel); if(!el)return null;
      function pc(s){const m=String(s||'').match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\)/i);return m?{r:+m[1],g:+m[2],b:+m[3],a:m[4]===undefined?1:+m[4]}:null}
      function over(f,b){if(!f)return b;const a=f.a+b.a*(1-f.a);return{r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}}
      function bg(node){const chain=[];for(let n=node;n;n=n.parentElement)chain.push(n);let c={r:255,g:255,b:255,a:1};for(let i=chain.length-1;i>=0;i--){const q=pc(getComputedStyle(chain[i]).backgroundColor);if(q)c=over(q,c)}return c}
      function L(c){const f=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)}
      function ratio(a,b){if(!a||!b)return null;const x=L(a),y=L(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
      const base=bg(el), cs=getComputedStyle(el,pseudo||null);
      const c=pc(pseudo?cs.backgroundColor:cs.color);
      const eff=c?over(c,base):null;
      return {selector:sel,pseudo,display:cs.display,color:cs.color,background:cs.backgroundColor,borderColor:cs.borderColor,appearance:cs.appearance||cs.webkitAppearance||'',colorScheme:cs.colorScheme||'',ratio:eff?+ratio(eff,base).toFixed(2):null};
    },{sel,pseudo});
  }
  const data={name,url,http:r&&r.status(),errors,probes:[]};
  if(after) await after({p,inject,measure,data});
  await ctx.close(); return data;
}
(async()=>{
 const facts={};
 facts.prod24 = fileFacts('/tmp/prod24/index.html',['onboarding-primary','sf-btn','sr-badge','APP_VERSION','--gold']);
 facts.test24 = fileFacts('24h-v119-b1-prephysical/index.html',['onboarding-primary','sf-btn','sr-badge','APP_VERSION','--gold']);
 facts.lettres29 = fileFacts('lettres-v2.9-b1-governed-r4/index.html',['const APP_VERSION','.help-topic-select','.path-step.done','.search-term-flash','.help-dot::after']);
 facts.lettres210 = fileFacts('lettres-v2.10-b1-prephysical/index.html',['const APP_VERSION','.help-topic-select','.path-step.done','.search-term-flash','.help-dot::after']);
 facts.ldc135 = fileFacts('ldc-v135-r8-governed-r7/index.html',['v2.19.135-R1B-UX-ACCESS-R8','search-mode-badge','help-chip.light','help-tip','autour-card-tag']);
 facts.marie46 = fileFacts('marie-v46/index.html',["const APP_VERSION = '46'",'.backup-btn.primary:hover','--primary-light']);
 console.log('FILE_FACTS',JSON.stringify(facts));

 const browser=await chromium.launch({headless:true});
 const out=[];
 out.push(await pageProbe(browser,'24H-PROD-v119','http://127.0.0.1:8766/',async({inject,measure,data})=>{
   for(const d of [['x1','button','onboarding-primary','Commencer'],['x2','button','sf-btn active','Actif'],['x3','span','sr-badge reflection','Réflexion'],['x4','span','sr-badge speech','Parole']]){await inject(...d);data.probes.push(await measure('#'+d[0]));}
   const ds=await (await browser.newContext()).newPage().catch(()=>null);
 }));
 out.push(await pageProbe(browser,'24H-APPTEST-SAMELABEL','http://127.0.0.1:8765/24h-v119-b1-prephysical/',async({inject,measure,data})=>{
   for(const d of [['x1','button','onboarding-primary','Commencer'],['x2','button','sf-btn active','Actif'],['x3','span','sr-badge reflection','Réflexion'],['x4','span','sr-badge speech','Parole']]){await inject(...d);data.probes.push(await measure('#'+d[0]));}
 }));
 out.push(await pageProbe(browser,'LDC-v135','http://127.0.0.1:8765/ldc-v135-r8-governed-r7/',async({p,inject,measure,data})=>{
   try{await p.evaluate(()=>typeof openHelp==='function'&&openHelp());await p.waitForTimeout(300)}catch(e){}
   for(const sel of ['.help-chip.light','.help-tip']){const n=await p.locator(sel).count();data.probes.push({realInstance:sel,count:n,measure:n?await measure(sel):null});}
   for(const d of [['x1','span','search-mode-badge','Mode'],['x2','span','rc-tag','Tag'],['x3','span','hsi-gold','Or'],['x4','span','autour-card-tag','Thème']]){await inject(...d);data.probes.push(await measure('#'+d[0]));}
 }));
 out.push(await pageProbe(browser,'Lettres-v2.10','http://127.0.0.1:8765/lettres-v2.10-b1-prephysical/',async({p,inject,measure,data})=>{
   try{await p.evaluate(()=>typeof openHelp==='function'&&openHelp());await p.waitForTimeout(300)}catch(e){}
   data.probes.push({helpSelect:await measure('#help-topic-select')});
   data.probes.push({searchSelect:await measure('#search-sort')});
   const dots=await p.locator('.help-dot').count(); data.probes.push({dots});
   if(dots){data.probes.push({dot0After:await measure('.help-dot','::after')});if(dots>1)data.probes.push({dot1After:await measure('.help-dot:nth-child(2)','::after')});}
   await inject('x1','span','path-step done','1');data.probes.push(await measure('#x1'));
   await inject('x2','span','search-term-flash','mot');data.probes.push(await measure('#x2'));
 }));
 out.push(await pageProbe(browser,'Marie-v46','http://127.0.0.1:8765/marie-v46/',async({p,inject,measure,data})=>{
   await inject('x1','button','backup-btn primary','Restaurer');data.probes.push({base:await measure('#x1')});await p.locator('#x1').hover();data.probes.push({hover:await measure('#x1')});
 }));
 await browser.close();
 console.log('PROBES',JSON.stringify(out));
 fs.writeFileSync('dark_mode_baseline_reconcile.json',JSON.stringify({facts,out},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
