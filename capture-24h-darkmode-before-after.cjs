const { chromium } = require('playwright');
const fs = require('fs');
const routes = [
  {label:'before_v119_B1', path:'24h-v119-b1-governed-r4'},
  {label:'after_v120_B4', path:'24h-v120-b4-darkmode'}
];
(async()=>{
  const browser = await chromium.launch({headless:true});
  fs.mkdirSync('24h-darkmode-screenshots-v2',{recursive:true});
  const metrics={};
  for (const r of routes){
    const ctx = await browser.newContext({colorScheme:'dark', viewport:{width:390,height:844}, deviceScaleFactor:2});
    const page = await ctx.newPage();
    const url='http://127.0.0.1:8080/'+r.path+'/';
    const res=await page.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
    if(!res || !res.ok()) throw new Error(r.label+' load failed');
    await page.waitForTimeout(1800);
    await page.evaluate(()=>{document.documentElement.setAttribute('data-theme','dark'); try{if(typeof showHome==='function')showHome();}catch(e){}});
    await page.waitForTimeout(400);
    await page.screenshot({path:'24h-darkmode-screenshots-v2/'+r.label+'_actual_home.png',fullPage:false});

    await page.evaluate(()=>{
      document.getElementById('qa-darkmode-proof')?.remove();
      const wrap=document.createElement('div');
      wrap.id='qa-darkmode-proof';
      Object.assign(wrap.style,{
        position:'fixed',inset:'0',zIndex:'2147483647',background:'var(--bg)',color:'var(--ink)',
        padding:'18px 16px 22px',overflow:'auto',fontFamily:'var(--font-ui)',boxSizing:'border-box'
      });
      const title=document.createElement('div');
      title.textContent='24H — surfaces modifiées en mode sombre';
      Object.assign(title.style,{fontFamily:'var(--font-display)',fontSize:'18px',fontWeight:'700',marginBottom:'16px',color:'var(--ink)'});
      wrap.appendChild(title);

      const section=(label)=>{
        const sec=document.createElement('section');
        Object.assign(sec.style,{background:'var(--bg2)',border:'1px solid var(--bg3)',borderRadius:'14px',padding:'14px',margin:'0 0 14px'});
        const lab=document.createElement('div'); lab.textContent=label;
        Object.assign(lab.style,{fontSize:'13px',fontWeight:'700',color:'var(--ink2)',marginBottom:'10px'});
        sec.appendChild(lab); wrap.appendChild(sec); return sec;
      };

      let sec=section('Bouton principal / filtre actif');
      const row=document.createElement('div'); Object.assign(row.style,{display:'flex',gap:'10px',alignItems:'center',flexWrap:'wrap'});
      const b1=document.createElement('button'); b1.className='onboarding-primary'; b1.textContent='Commencer';
      const b2=document.createElement('button'); b2.className='sf-btn active'; b2.textContent='Actif';
      row.append(b1,b2); sec.appendChild(row);

      sec=section('Badges de texte');
      const row2=document.createElement('div'); Object.assign(row2.style,{display:'flex',gap:'10px',alignItems:'center',flexWrap:'wrap'});
      const br=document.createElement('span'); br.className='sr-badge reflection'; br.textContent='Réflexion';
      const bs=document.createElement('span'); bs.className='sr-badge speech'; bs.textContent='Parole';
      row2.append(br,bs); sec.appendChild(row2);

      sec=section('Texte descriptif secondaire');
      const card=document.createElement('button'); card.className='stage6m-home-action';
      Object.assign(card.style,{width:'100%',display:'block'});
      card.innerHTML='<div class="k">Guide</div><div class="t">Comment pratiquer</div><div class="d">Une Heure par jour, heure réelle ou parcours libre.</div>';
      sec.appendChild(card);

      sec=section('Navigation inférieure');
      const nav=document.createElement('div'); nav.className='bottom-nav qa-bottom';
      Object.assign(nav.style,{position:'static',display:'flex',width:'100%',borderRadius:'10px',overflow:'hidden',paddingBottom:'0',minHeight:'66px'});
      const items=[
        ['active','Accueil','<circle cx="12" cy="12" r="8"/>'],
        ['', 'Heures','<path d="M4 6h16M4 12h16M4 18h16"/>'],
        ['', 'Recherche','<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>'],
        ['', 'Mon Espace','<circle cx="12" cy="8" r="3"/><path d="M5 21c1-5 13-5 14 0"/>']
      ];
      for(const [active,label,svg] of items){
        const btn=document.createElement('button');btn.className='bn-item '+active;
        Object.assign(btn.style,{fontSize:'13px'});
        btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:22px;height:22px">'+svg+'</svg><span>'+label+'</span>';
        nav.appendChild(btn);
      }
      sec.appendChild(nav);
      document.body.appendChild(wrap);
    });
    await page.waitForTimeout(200);
    await page.locator('#qa-darkmode-proof').screenshot({path:'24h-darkmode-screenshots-v2/'+r.label+'_changed_surfaces.png'});

    metrics[r.label]=await page.evaluate(()=>{
      const sels={primary:'.onboarding-primary',active_filter:'.sf-btn.active',reflection:'.sr-badge.reflection',speech:'.sr-badge.speech',description:'.stage6m-home-action .d',nav_active:'.qa-bottom .bn-item.active',nav_inactive:'.qa-bottom .bn-item:not(.active)'};
      const out={};
      for(const [k,sel] of Object.entries(sels)){const el=document.querySelector('#qa-darkmode-proof '+sel);if(el){const s=getComputedStyle(el);out[k]={color:s.color,background:s.backgroundColor,borderColor:s.borderColor};}}
      return out;
    });
    await ctx.close();
  }
  fs.writeFileSync('24h-darkmode-screenshots-v2/metrics.json',JSON.stringify(metrics,null,2));
  await browser.close();
  console.log('SCREENSHOT_CAPTURE_V2_PASS');
})().catch(e=>{console.error(e);process.exit(1)});