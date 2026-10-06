const {chromium}=require('playwright');const axe=require('axe-core'),fs=require('fs');
const ROUTE='24h-v120-b7-adversarial';
(async()=>{
 const b=await chromium.launch({headless:true});const out={scenes:[]};let totalViol=0;
 for(const scheme of ['light','dark']){
  const c=await b.newContext({colorScheme:scheme,viewport:{width:390,height:844}});const p=await c.newPage();const errs=[];
  p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://127.0.0.1:8092/'+ROUTE+'/',{waitUntil:'domcontentloaded'});await p.waitForTimeout(700);
  async function auditScene(name,setup){
    if(setup)await setup();await p.waitForTimeout(150);
    await p.evaluate(axe.source);
    const r=await p.evaluate(async()=>{const a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});return{
      violations:a.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.slice(0,12).map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))})),
      overflow:document.documentElement.scrollWidth-window.innerWidth,
      focusables:[...document.querySelectorAll('button,a[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'}).length,
      text:(document.querySelector('#content')?.innerText||document.body.innerText||'').slice(0,220)
    }});
    totalViol+=r.violations.length;out.scenes.push({scheme,name,...r});
  }
  await auditScene('home',async()=>p.evaluate(()=>showHome()));
  await auditScene('hours',async()=>p.evaluate(()=>showHoursView()));
  await auditScene('reader-hour1',async()=>p.evaluate(()=>openHour(1)));
  const tabs=p.locator('[role="tab"],.tab-btn:visible');const n=Math.min(await tabs.count(),8);
  for(let i=0;i<n;i++){
    await tabs.nth(i).click({force:true}).catch(()=>{});await auditScene('reader-tab-'+i,null);
  }
  await auditScene('search',async()=>{await p.evaluate(()=>showSearchView());const q=p.locator('input[type="search"],input.search-input,input[placeholder*="Recher"]').first();if(await q.count()){await q.fill('volonté');await q.dispatchEvent('input');await p.waitForTimeout(300)}});
  await auditScene('espace',async()=>p.evaluate(()=>showEspaceView()));
  await auditScene('help',async()=>p.evaluate(()=>showHelp()));
  await p.keyboard.press('Escape').catch(()=>{});
  await auditScene('settings',async()=>p.evaluate(()=>showSettingsSheet()));
  await p.keyboard.press('Escape').catch(()=>{});
  await auditScene('prayer',async()=>p.evaluate(()=>openPrayer('PASSION24.PRAYER.BEFORE_EACH_HOUR')));
  await p.keyboard.press('Escape').catch(()=>{});
  if(typeof (await p.evaluate(()=>typeof showProvenance))==='string'){}
  out.scenes.push({scheme,name:'runtime-errors',errors:errs});
  await c.close();
 }
 await b.close();fs.writeFileSync('24h-b7-independent-rendered-sweep.json',JSON.stringify(out,null,2));
 console.log('SCENES',out.scenes.length,'AXE_VIOLATIONS',totalViol);
 if(totalViol)process.exit(2);
 const errs=out.scenes.flatMap(x=>x.errors||[]).filter(x=>/content security policy|uncaught|referenceerror|typeerror/i.test(x));
 if(errs.length){console.error(errs);process.exit(3)}
})().catch(e=>{console.error(e);process.exit(1)});