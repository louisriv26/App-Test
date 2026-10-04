const {chromium}=require('playwright');
const fs=require('fs');
const SRC46='marie-v46', SRC48='marie-v48-b3-csp-note-placeholder-closure', DST='qa-marie-v48b3-upgrade';
const BASE='http://127.0.0.1:8081/'+DST+'/';
function cp(src){fs.rmSync(DST,{recursive:true,force:true});fs.cpSync(src,DST,{recursive:true});}
async function ready(p,version){
  await p.waitForFunction(v=>{
    const l=document.getElementById('screen-loading'), mv=document.getElementById('mobile-version');
    return typeof APP_VERSION!=='undefined' && APP_VERSION===v && typeof State!=='undefined' &&
      Array.isArray(State.corpus)&&State.corpus.length===37 && l&&!l.classList.contains('active') &&
      mv&&mv.textContent==='v'+v;
  },version,{timeout:30000});
}
(async()=>{
  cp(SRC46);
  const b=await chromium.launch({headless:true});
  const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
  await c.addInitScript(()=>localStorage.setItem('mjv_onboarded','1'));
  let errors=[]; const attach=p=>{p.on('pageerror',e=>errors.push('PAGE '+String(e)));p.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE '+m.text())})};
  let p=await c.newPage();attach(p);
  await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});await ready(p,'46');
  await p.waitForFunction(()=>!!navigator.serviceWorker.controller,{timeout:30000}).catch(()=>{});
  // Create representative valid durable state through the app controls.
  await p.click('.cal-cell[data-day="1"]');await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
  const unit=await p.evaluate(()=>currentUnit().unit_id);
  await p.click('#btn-complete');await p.click('#btn-activate');
  await p.click('#btn-textsize');await p.click('#textsize-panel .textsize-option[data-text-level="xlarge"]');
  const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
  await p.locator('#reader-body .para-note-btn').first().click();
  await p.fill('#note-textarea','QA_MARIE_UPGRADE_SENTINEL');await p.click('#note-modal .modal-btn-save');
  await p.evaluate(()=>localStorage.setItem('APP_GOV_MARIE_UPGRADE_SENTINEL','PRESERVE_ME'));
  const pre=await p.evaluate(unit=>({
    v:APP_VERSION,read:State.read.has(unit),activeDay:State.activeDay,textSize:State.textSize,
    note:Object.values(State.notes).some(n=>n.text==='QA_MARIE_UPGRADE_SENTINEL'),
    sentinel:localStorage.getItem('APP_GOV_MARIE_UPGRADE_SENTINEL'),
    versionText:document.getElementById('mobile-version').textContent
  }),unit);
  if(pre.v!=='46'||!pre.read||pre.activeDay!==1||pre.textSize!=='xlarge'||!pre.note||pre.sentinel!=='PRESERVE_ME')
    throw new Error('predecessor state setup failed '+JSON.stringify(pre));

  // Replace server bytes with the exact B2 successor and force the registered worker to check.
  cp(SRC48);
  await p.evaluate(async()=>{
    const r=await navigator.serviceWorker.getRegistration();
    if(!r)throw new Error('no predecessor service worker registration');
    await r.update();
    await new Promise(resolve=>setTimeout(resolve,2500));
  });
  await p.close(); await new Promise(r=>setTimeout(r,700));
  p=await c.newPage();attach(p);
  await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:120000});await ready(p,'48');
  const post=await p.evaluate(unit=>({
    v:APP_VERSION,read:State.read.has(unit),activeDay:State.activeDay,textSize:State.textSize,
    note:Object.values(State.notes).some(n=>n.text==='QA_MARIE_UPGRADE_SENTINEL'),
    sentinel:localStorage.getItem('APP_GOV_MARIE_UPGRADE_SENTINEL'),
    loading:document.getElementById('screen-loading').classList.contains('active'),
    versionText:document.getElementById('mobile-version').textContent,
    controller:!!navigator.serviceWorker.controller,
    caches:null
  }),unit);
  post.caches=await p.evaluate(()=>caches.keys());
  if(post.v!=='48'||!post.read||post.activeDay!==1||post.textSize!=='xlarge'||!post.note||post.sentinel!=='PRESERVE_ME'||post.loading||post.versionText!=='v48'||!post.controller)
    throw new Error('successor online state failed '+JSON.stringify(post));
  if(!post.caches.some(x=>/-shell-v48$/.test(x))||!post.caches.some(x=>/-content-v3$/.test(x)))
    throw new Error('successor caches missing '+JSON.stringify(post.caches));

  // Two cold offline reopens must be genuinely ready, not merely a successful HTTP/navigation.
  await c.setOffline(true);
  const offline=[];
  for(let i=0;i<2;i++){
    await p.close();p=await c.newPage();attach(p);
    await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:30000});await ready(p,'48');
    const x=await p.evaluate(unit=>({
      v:APP_VERSION,read:State.read.has(unit),activeDay:State.activeDay,textSize:State.textSize,
      note:Object.values(State.notes).some(n=>n.text==='QA_MARIE_UPGRADE_SENTINEL'),
      sentinel:localStorage.getItem('APP_GOV_MARIE_UPGRADE_SENTINEL'),
      loading:document.getElementById('screen-loading').classList.contains('active'),
      versionText:document.getElementById('mobile-version').textContent
    }),unit);
    if(x.v!=='48'||!x.read||x.activeDay!==1||x.textSize!=='xlarge'||!x.note||x.sentinel!=='PRESERVE_ME'||x.loading||x.versionText!=='v48')
      throw new Error('offline reopen '+i+' failed '+JSON.stringify(x));
    offline.push(x);
  }
  await c.setOffline(false);await p.reload({waitUntil:'domcontentloaded',timeout:120000});await ready(p,'48');
  const recovery=await p.evaluate(()=>({v:APP_VERSION,loading:document.getElementById('screen-loading').classList.contains('active'),versionText:document.getElementById('mobile-version').textContent}));
  const bad=errors.filter(x=>/content security policy|refused to execute|refused to apply|uncaught|referenceerror|typeerror|syntaxerror/i.test(x));
  if(bad.length)throw new Error('successor PWA/runtime errors '+JSON.stringify(bad));
  const out={candidate:'MJV v48/B3',pre,post,offline,recovery,errors,status:'PASS'};
  fs.writeFileSync('MJV_v48_B3_PWA_UPDATE_OFFLINE_EVIDENCE.json',JSON.stringify(out,null,2));
  await c.close();await b.close();
  console.log('MARIE_V46_TO_V48_B2_PWA_PASS');
})().catch(e=>{console.error(e);process.exit(2)});