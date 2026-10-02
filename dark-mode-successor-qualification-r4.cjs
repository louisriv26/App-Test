const { chromium } = require('playwright');
const fs = require('fs');
const apps = [
  {name:'24H', path:'24h-v120-b3-darkmode'},
  {name:'LDC', path:'ldc-v136-r9-darkmode'},
  {name:'Lettres', path:'lettres-v2.12-b1-darkmode'},
  {name:'Marie', path:'marie-v47-b1-darkmode'}
];
function fail(msg){ throw new Error(msg); }
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results={generated_at:new Date().toISOString(),apps:{}};
 const persist=()=>fs.writeFileSync('dark-mode-successor-qualification-r4-results.json',JSON.stringify(results,null,2));
 for(const app of apps){
  const ctx=await browser.newContext({colorScheme:'dark',viewport:{width:1180,height:900}});
  const p=await ctx.newPage();
  const errors=[]; const consoleErrors=[];
  p.on('pageerror',e=>errors.push(e.message));
  p.on('console',m=>{ if(m.type()==='error') consoleErrors.push(m.text()); });
  const url='http://127.0.0.1:8080/'+app.path+'/';
  const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
  if(!r || !r.ok()) fail(app.name+' HTTP load failed');
  await p.waitForTimeout(1200);
  await p.evaluate(()=>document.documentElement.setAttribute('data-theme','dark'));
  await p.waitForTimeout(150);

  async function inject(id,tag,cls,text){
   await p.evaluate(({id,tag,cls,text})=>{
    document.getElementById(id)?.remove();
    const el=document.createElement(tag); el.id=id; el.className=cls; el.textContent=text;
    el.style.position='fixed'; el.style.left='10px'; el.style.top='10px'; el.style.zIndex='2147483647';
    document.body.appendChild(el);
   },{id,tag,cls,text});
  }
  async function measure(sel,pseudo=null){
   return await p.evaluate(({sel,pseudo})=>{
    const el=document.querySelector(sel); if(!el) return null;
    const parse=s=>{const n=String(s||'').match(/[0-9.]+/g);if(!n||n.length<3)return null;return {r:+n[0],g:+n[1],b:+n[2],a:n[3]===undefined?1:+n[3]};};
    const comp=(f,b)=>{const a=f.a+b.a*(1-f.a);return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a};};
    const lum=c=>{const z=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*z(c.r)+.7152*z(c.g)+.0722*z(c.b)};
    const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
    const bgOf=node=>{const chain=[];let n=node;while(n&&n.nodeType===1){chain.unshift(n);n=n.parentElement}let b={r:255,g:255,b:255,a:1};for(const x of chain){const q=parse(getComputedStyle(x).backgroundColor);if(q&&q.a>0)b=comp(q,b)}return b};
    const bg=bgOf(el), cs=getComputedStyle(el,pseudo);
    const fg=parse(cs.color), pb=parse(cs.backgroundColor);
    const effectiveBg=pb&&pb.a>0?comp(pb,bg):bg;
    const effectiveFg=fg?comp(fg,effectiveBg):null;
    return {ratio:effectiveFg?+ratio(effectiveFg,effectiveBg).toFixed(2):null,color:cs.color,background:cs.backgroundColor,borderColor:cs.borderColor,appearance:cs.appearance||cs.webkitAppearance||'',colorScheme:cs.colorScheme||'',backgroundImage:cs.backgroundImage||'',outline:cs.outline};
   },{sel,pseudo});
  }
  const out={url,errors,consoleErrors,checks:{}};
  const requireRatio=(key,m,min)=>{out.checks[key]=m;if(!m||m.ratio<min)fail(app.name+' '+key+' ratio '+(m&&m.ratio)+' < '+min);};

  if(app.name==='24H'){
   await inject('q1','button','onboarding-primary','Commencer'); requireRatio('onboarding',await measure('#q1'),4.5);
   await inject('q2','button','sf-btn active','Actif'); requireRatio('sf_active',await measure('#q2'),4.5);
   await inject('q3','span','sr-badge reflection','Réflexion'); requireRatio('reflection_badge',await measure('#q3'),4.5);
   await inject('q4','span','sr-badge speech','Parole'); requireRatio('speech_badge',await measure('#q4'),4.5);
   await p.evaluate(()=>{const wrap=document.createElement('button');wrap.className='stage6m-home-action';wrap.id='q5wrap';wrap.style.position='fixed';wrap.style.left='10px';wrap.style.top='10px';wrap.style.zIndex='2147483647';const d=document.createElement('div');d.id='q5';d.className='d';d.textContent='Description secondaire';wrap.appendChild(d);document.body.appendChild(wrap)}); requireRatio('secondary_description',await measure('#q5'),4.5);
  }
  if(app.name==='LDC'){
   for(const [id,cls] of [['q1','search-mode-badge'],['q2','rc-tag'],['q3','rc-tag approximate'],['q4','hsi-gold'],['q5','help-chip light'],['q6','help-tip'],['q7','autour-card-tag']]){
    await inject(id,'span',cls,'Étiquette'); requireRatio(cls,await measure('#'+id),4.5);
   }
   for(const [id,cls] of [['q8','st-luisa'],['q9','rc-btn'],['q10','btn-primary']]){
    await inject(id,cls.includes('btn')?'button':'span',cls,'Contrôle'); requireRatio('known_good_'+cls,await measure('#'+id),4.5);
   }
  }
  if(app.name==='Lettres'){
   try{await p.evaluate(()=>typeof openHelp==='function'&&openHelp());await p.waitForTimeout(150);}catch(e){}
   for(const sel of ['.help-topic-select','#search-sort']){
    const m=await measure(sel); out.checks['select_'+sel]=m;
    if(!m) fail('Lettres missing '+sel);
    if(m.appearance!=='none') fail('Lettres '+sel+' appearance='+m.appearance);
    if(!/dark/.test(m.colorScheme)) fail('Lettres '+sel+' colorScheme='+m.colorScheme);
    if(!m.backgroundImage || m.backgroundImage==='none') fail('Lettres '+sel+' custom disclosure absent');
   }
   await inject('q1','span','path-step done','1'); requireRatio('path_step_done',await measure('#q1'),4.5);
   await inject('q2','span','search-term-flash','mot recherché'); requireRatio('search_term_flash',await measure('#q2'),4.5);
   const count=await p.locator('.help-dot').count(); if(count<2) fail('Lettres help dots unavailable');
   await p.locator('.help-dot').nth(1).evaluate(el=>el.id='qdot');
   const dot=await p.evaluate(()=>{
    const el=document.querySelector('#qdot'), foot=el.closest('.help-footer');
    const parse=s=>{const n=String(s||'').match(/[0-9.]+/g);return n?{r:+n[0],g:+n[1],b:+n[2],a:n[3]===undefined?1:+n[3]}:null};
    const comp=(f,b)=>{const a=f.a+b.a*(1-f.a);return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a}};
    const lum=c=>{const z=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*z(c.r)+.7152*z(c.g)+.0722*z(c.b)};
    const cr=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
    let bg={r:255,g:255,b:255,a:1}, chain=[];let n=foot;while(n){chain.unshift(n);n=n.parentElement}for(const x of chain){const q=parse(getComputedStyle(x).backgroundColor);if(q&&q.a>0)bg=comp(q,bg)}
    const q=parse(getComputedStyle(el,'::after').backgroundColor); const dot=q?comp(q,bg):null;
    return {ratio:dot?+cr(dot,bg).toFixed(2):null,pseudo:getComputedStyle(el,'::after').backgroundColor,footer:getComputedStyle(foot).backgroundColor};
   });
   out.checks.help_dot_inactive=dot; if(!dot||dot.ratio<3) fail('Lettres help dot ratio '+(dot&&dot.ratio)+' < 3');
  }
  if(app.name==='Marie'){
   await inject('q1','button','backup-btn primary','Restaurer'); requireRatio('backup_base',await measure('#q1'),4.5);
   await p.locator('#q1').hover(); requireRatio('backup_hover',await measure('#q1'),4.5);
   await p.locator('#q1').focus(); requireRatio('backup_focus',await measure('#q1'),4.5);
  }

  if(errors.length) fail(app.name+' page errors: '+errors.join(' | '));
  results.apps[app.name]=out;
  persist();
  await ctx.close();
 }
 await browser.close();
 persist();
 console.log('DARK_MODE_SUCCESSOR_QUALIFICATION_PASS');
})().catch(e=>{try{fs.writeFileSync('dark-mode-successor-qualification-r4-results.json',JSON.stringify(results,null,2))}catch(_){} console.error(e);process.exit(1)});