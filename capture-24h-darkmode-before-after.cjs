const { chromium } = require('playwright');
const fs = require('fs');
const routes = [
  {label:'before_v119_B1', path:'24h-v119-b1-governed-r4'},
  {label:'after_v120_B4', path:'24h-v120-b4-darkmode'}
];
(async()=>{
  const browser = await chromium.launch({headless:true});
  fs.mkdirSync('24h-darkmode-screenshots',{recursive:true});
  const metrics={};
  for (const r of routes){
    const ctx = await browser.newContext({colorScheme:'dark', viewport:{width:390,height:844}, deviceScaleFactor:2});
    const page = await ctx.newPage();
    const url='http://127.0.0.1:8080/'+r.path+'/';
    const res=await page.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
    if(!res || !res.ok()) throw new Error(r.label+' load failed');
    await page.waitForTimeout(1800);
    await page.evaluate(()=>{document.documentElement.setAttribute('data-theme','dark'); try{if(typeof showHome==='function')showHome();}catch(e){}});
    await page.waitForTimeout(500);
    await page.screenshot({path:'24h-darkmode-screenshots/'+r.label+'_actual_home.png',fullPage:false});

    await page.evaluate(()=>{
      document.getElementById('qa-darkmode-proof')?.remove();
      const wrap=document.createElement('div');
      wrap.id='qa-darkmode-proof';
      wrap.innerHTML=`
        <div class="qa-title">24H — surfaces modifiées en mode sombre</div>
        <section>
          <div class="qa-label">Bouton principal / filtre actif</div>
          <div class="qa-row">
            <button class="onboarding-primary">Commencer</button>
            <button class="sf-btn active">Actif</button>
          </div>
        </section>
        <section>
          <div class="qa-label">Badges de texte</div>
          <div class="qa-row">
            <span class="sr-badge reflection">Réflexion</span>
            <span class="sr-badge speech">Parole</span>
          </div>
        </section>
        <section>
          <div class="qa-label">Texte descriptif secondaire</div>
          <button class="stage6m-home-action qa-home-action">
            <div class="k">Guide</div>
            <div class="t">Comment pratiquer</div>
            <div class="d">Une Heure par jour, heure réelle ou parcours libre.</div>
          </button>
        </section>
        <section>
          <div class="qa-label">Navigation inférieure</div>
          <div class="bottom-nav qa-bottom">
            <button class="bn-item active"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg><span>Accueil</span></button>
            <button class="bn-item"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span>Heures</span></button>
            <button class="bn-item"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><span>Recherche</span></button>
            <button class="bn-item"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="3"/><path d="M5 21c1-5 13-5 14 0"/></svg><span>Mon Espace</span></button>
          </div>
        </section>`;
      const style=document.createElement('style');
      style.textContent=`
        #qa-darkmode-proof{position:fixed;inset:0;z-index:2147483647;background:var(--bg);color:var(--ink);padding:18px 16px 22px;overflow:auto;font-family:var(--font-ui);box-sizing:border-box}
        #qa-darkmode-proof .qa-title{font-family:var(--font-display);font-size:18px;font-weight:700;margin-bottom:16px;color:var(--ink)}
        #qa-darkmode-proof section{background:var(--bg2);border:1px solid var(--bg3);border-radius:14px;padding:14px;margin:0 0 14px}
        #qa-darkmode-proof .qa-label{font-size:13px;font-weight:700;color:var(--ink2);margin-bottom:10px}
        #qa-darkmode-proof .qa-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
        #qa-darkmode-proof .qa-home-action{width:100%;display:block}
        #qa-darkmode-proof .qa-bottom{position:static!important;display:flex!important;width:100%;border-radius:10px;overflow:hidden;padding-bottom:0!important;min-height:66px!important}
        #qa-darkmode-proof .qa-bottom .bn-item{font-size:13px!important}
        #qa-darkmode-proof .qa-bottom .bn-item svg{width:22px!important;height:22px!important}
      `;
      document.head.appendChild(style);
      document.body.appendChild(wrap);
    });
    await page.waitForTimeout(200);
    await page.locator('#qa-darkmode-proof').screenshot({path:'24h-darkmode-screenshots/'+r.label+'_changed_surfaces.png'});

    metrics[r.label]=await page.evaluate(()=>{
      const sels={primary:'.onboarding-primary',active_filter:'.sf-btn.active',reflection:'.sr-badge.reflection',speech:'.sr-badge.speech',description:'.stage6m-home-action .d',nav_active:'.qa-bottom .bn-item.active',nav_inactive:'.qa-bottom .bn-item:not(.active)'};
      const out={};
      for(const [k,sel] of Object.entries(sels)){const el=document.querySelector('#qa-darkmode-proof '+sel);if(el){const s=getComputedStyle(el);out[k]={color:s.color,background:s.backgroundColor,borderColor:s.borderColor};}}
      return out;
    });
    await ctx.close();
  }
  fs.writeFileSync('24h-darkmode-screenshots/metrics.json',JSON.stringify(metrics,null,2));
  await browser.close();
  console.log('SCREENSHOT_CAPTURE_PASS');
})().catch(e=>{console.error(e);process.exit(1)});