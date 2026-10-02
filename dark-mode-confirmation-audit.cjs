const { chromium } = require('playwright');

const apps=[
 {name:'24H',url:'https://louisriv26.github.io/App-Test/24h-v119-b1-prephysical/'},
 {name:'LDC',url:'https://louisriv26.github.io/App-Test/ldc-v135-r8-governed-r7/'},
 {name:'Lettres',url:'https://louisriv26.github.io/App-Test/lettres-v2.10-b1-prephysical/'},
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

   const core=await p.evaluate(()=>{
     function parse(s){
       const nums=String(s||'').match(/[0-9.]+/g); if(!nums||nums.length<3)return null;
       return {r:+nums[0],g:+nums[1],b:+nums[2],a:nums[3]===undefined?1:+nums[3]};
     }
     function over(f,b){const a=f.a+b.a*(1-f.a);if(!a)return {r:0,g:0,b:0,a:0};return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a};}
     function bg(el){
       const chain=[];let n=el;while(n&&n.nodeType===1){chain.unshift(n);n=n.parentElement}
       let c={r:255,g:255,b:255,a:1};
       for(const x of chain){const q=parse(getComputedStyle(x).backgroundColor);if(q&&q.a>0)c=over(q,c)}
       return c;
     }
     function fg(el,b){const q=parse(getComputedStyle(el).color);return q?over(q,b):null}
     function lum(c){const f=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)}
     function cr(a,b){const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
     function rgb(c){return 'rgb('+Math.round(c.r)+','+Math.round(c.g)+','+Math.round(c.b)+')'}
     function measure(el){
       const b=bg(el),f=fg(el,b),cs=getComputedStyle(el);
       return {color:cs.color,background:cs.backgroundColor,effectiveBg:rgb(b),ratio:f?+cr(f,b).toFixed(2):null,appearance:cs.appearance||cs.webkitAppearance||'',colorScheme:cs.colorScheme||'',borderColor:cs.borderColor};
     }
     return {theme:document.documentElement.getAttribute('data-theme'),title:document.title,
       nativeSelects:[...document.querySelectorAll('select')].map(el=>({id:el.id,cls:el.className,aria:el.getAttribute('aria-label')||'',...measure(el)}))
     };
   });

   const probes=[];
   async function inject(id,tag,cls,text,attrs={}){
     await p.evaluate(({id,tag,cls,text,attrs})=>{
       const old=document.getElementById(id);if(old)old.remove();
       const el=document.createElement(tag);el.id=id;el.className=cls;el.textContent=text;
       for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);
       el.style.position='fixed';el.style.left='10px';el.style.top='10px';el.style.zIndex='2147483647';
       document.body.appendChild(el);
     },{id,tag,cls,text,attrs});
   }
   async function measure(id,label,state='base'){
     const val=await p.evaluate(id=>{
       const el=document.getElementById(id);
       function parse(s){const nums=String(s||'').match(/[0-9.]+/g);if(!nums||nums.length<3)return null;return {r:+nums[0],g:+nums[1],b:+nums[2],a:nums[3]===undefined?1:+nums[3]};}
       function over(f,b){const a=f.a+b.a*(1-f.a);return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.b*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a};}
       // corrected over function locally below (avoid typo effects by inline recompute)
       function comp(f,b){const a=f.a+b.a*(1-f.a);return {r:(f.r*f.a+b.r*b.a*(1-f.a))/a,g:(f.g*f.a+b.g*b.a*(1-f.a))/a,b:(f.b*f.a+b.b*b.a*(1-f.a))/a,a};}
       const chain=[];let n=el;while(n&&n.nodeType===1){chain.unshift(n);n=n.parentElement}
       let bg={r:255,g:255,b:255,a:1};for(const x of chain){const q=parse(getComputedStyle(x).backgroundColor);if(q&&q.a>0)bg=comp(q,bg)}
       const cs=getComputedStyle(el),fc=parse(cs.color),fg=fc?comp(fc,bg):null;
       const lum=c=>{const f=v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)};
       const ratio=fg?(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05):null;
       return {color:cs.color,background:cs.backgroundColor,effectiveBg:'rgb('+Math.round(bg.r)+','+Math.round(bg.g)+','+Math.round(bg.b)+')',ratio:ratio?+ratio.toFixed(2):null,borderColor:cs.borderColor,appearance:cs.appearance||cs.webkitAppearance||'',colorScheme:cs.colorScheme||''};
     },id);
     probes.push({label,state,...val});
   }

   if(app.name==='24H'){
     const defs=[
       ['p1','button','onboarding-primary','Commencer la 1re Heure →',{}],
       ['p2','button','resume-panel-btn primary','Ouvrir la recherche',{}],
       ['p3','button','sf-btn active','Actif',{'aria-pressed':'true'}],
       ['p4','button','mark-btn','Marquer',{}],
       ['p5','div','update-banner','Nouvelle version disponible',{}],
       ['p6','button','cc-btn cc-primary','Continuer',{}],
       ['p7','button','note-save-btn','Enregistrer',{}],
       ['p8','button','library-quick-chip active','Filtre actif',{}],
       ['p9','button','theme-pref-btn active','Sombre',{}],
       ['p10','button','library-title-mark-btn','Marquer titre',{'aria-pressed':'true'}],
       ['p11','button','integrity-btn','Vérifier',{}],
       ['p12','button','help-round','?',{}],
       ['p13','button','panel-close-btn','Fermer',{}],
       ['p14','button','hour-end-btn primary','Suivant',{}],
       ['p15','a','skip-link','Aller au contenu',{}],
       ['p16','span','sr-badge reflection','Réflexion',{}],
       ['p17','span','sr-badge speech','Parole',{}]
     ];
     for(const d of defs){await inject(...d);await measure(d[0],d[2]);}
     for(const [id,label] of [['p11','integrity-btn'],['p12','help-round'],['p13','panel-close-btn']]){await p.locator('#'+id).hover({force:true});await measure(id,label,'hover');}
   } else if(app.name==='LDC'){
     const defs=[
       ['p1','span','search-mode-badge','Mode',{}],
       ['p2','span','rc-tag','Tag',{}],
       ['p3','span','rc-tag approximate','Approximatif',{}],
       ['p4','span','hsi-gold','Or',{}],
       ['p5','span','help-chip light','Aide',{}],
       ['p6','div','help-tip','Conseil',{}],
       ['p7','span','autour-card-tag','Thème',{}],
       ['p8','span','st-luisa','Luisa',{}],
       ['p9','button','rc-btn','Reprendre',{}],
       ['p10','button','btn-primary','Enregistrer',{}]
     ];
     for(const d of defs){await inject(...d);await measure(d[0],d[2]);}
   } else if(app.name==='Lettres'){
     try{await p.evaluate(()=>typeof openHelp==='function'&&openHelp());await p.waitForTimeout(250)}catch(e){}
     const dots=await p.locator('.help-dot').count();
     if(dots){for(const idx of [0,Math.min(1,dots-1)]){const id='audit-dot-'+idx;await p.locator('.help-dot').nth(idx).evaluate((el,id)=>el.id=id,id);await measure(id,idx===0?'help-dot-active':'help-dot-inactive');}}
     await inject('p1','span','path-step done','1',{});await measure('p1','path-step.done');
     await inject('p2','span','search-term-flash','mot recherché',{});await measure('p2','search-term-flash');
     await inject('p3','span','topic-pill','Thème',{});await measure('p3','topic-pill');
   } else if(app.name==='Marie'){
     await inject('p1','button','backup-btn primary','Restaurer',{});await measure('p1','backup-btn.primary');
     await p.locator('#p1').hover();await measure('p1','backup-btn.primary','hover');
   }

   console.log('APP',app.name,'HTTP',r&&r.status(),'ERRORS',errors.length);
   console.log(' CORE',JSON.stringify(core));
   for(const q of probes) console.log(' PROBE',JSON.stringify(q));
   await ctx.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});