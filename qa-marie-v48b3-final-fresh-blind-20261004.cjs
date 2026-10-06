const { chromium } = require('playwright');
const fs=require('fs');
const ROOT='qa-marie-v48b3-finalblind-package';
const BASE='http://127.0.0.1:8092/'+ROOT+'/';

async function ready(p){
  await p.waitForFunction(()=>{
    const l=document.getElementById('screen-loading'),m=document.getElementById('mobile-version');
    return typeof APP_VERSION!=='undefined'&&APP_VERSION==='48'&&typeof State!=='undefined'&&Array.isArray(State.corpus)&&State.corpus.length===37&&l&&!l.classList.contains('active')&&m&&m.textContent==='v48';
  },null,{timeout:30000});
}
function qualifying(xs){return xs.filter(x=>/content security policy|refused|uncaught|referenceerror|typeerror|syntaxerror/i.test(x))}
async function errorsOn(p,xs){p.on('pageerror',e=>xs.push('PAGE '+String(e)));p.on('console',m=>{if(m.type()==='error')xs.push('CONSOLE '+m.text())})}
async function core(p,label){
  const x=await p.evaluate(()=>({v:APP_VERSION,corpus:State.corpus.length,self:App.selfTest(),sw:!!navigator.serviceWorker,loading:document.getElementById('screen-loading').classList.contains('active'),w:[document.documentElement.scrollWidth,document.documentElement.clientWidth]}));
  if(x.v!=='48'||x.corpus!==37||x.loading||x.self.total!==156||x.self.passed!==156||x.self.failed.length||x.w[0]>x.w[1]+1)throw new Error(label+' core '+JSON.stringify(x)); return x;
}

(async()=>{
 const b=await chromium.launch({headless:true});
 const out={candidate:'MJV v48/B3 final fresh blind',breakpoints:[],rangeHighlight:null,restore:null,status:'FAIL'};

 // A. Responsive threshold falsification: 767 mobile, 768 wide, 844x390 forced-mobile by height.
 for(const sc of [
   {name:'767-mobile',w:767,h:900,wide:false},
   {name:'768-wide',w:768,h:900,wide:true},
   {name:'landscape-short',w:844,h:390,wide:false}
 ]){
   const c=await b.newContext({viewport:{width:sc.w,height:sc.h},colorScheme:'dark'});
   await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
   const p=await c.newPage(), errs=[];await errorsOn(p,errs);await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});await ready(p);const cx=await core(p,sc.name);
   const layout=await p.evaluate(()=>({app:getComputedStyle(document.getElementById('app')).display,wide:getComputedStyle(document.getElementById('wide-shell')).display}));
   if(sc.wide){if(layout.app!=='none'||layout.wide==='none')throw new Error(sc.name+' wrong wide layout '+JSON.stringify(layout));await p.click('#wnav-search');await p.fill('#wide-search-input','Fiat');await p.waitForSelector('#wide-list-scroll .snippet-card');}
   else {if(layout.app==='none'||layout.wide!=='none')throw new Error(sc.name+' wrong mobile layout '+JSON.stringify(layout));await p.click('#nav-search');await p.fill('#search-input','Fiat');await p.waitForSelector('#list-scroll .snippet-card');}
   const count=sc.wide?await p.locator('#wide-list-scroll .snippet-card').count():await p.locator('#list-scroll .snippet-card').count();if(count<1)throw new Error(sc.name+' search empty');
   const bad=qualifying(errs);if(bad.length)throw new Error(sc.name+' errors '+JSON.stringify(bad));
   out.breakpoints.push({scene:sc,core:cx,layout,results:count,errors:errs});await c.close();
 }

 // B. Fresh partial-text selection/highlight path, then reload persistence.
 {
   const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
   await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
   let p=await c.newPage(),errs=[];await errorsOn(p,errs);await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});await ready(p);await core(p,'range');
   await p.click('.cal-cell[data-day="1"]');await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
   const pid=await p.locator('#reader-body p[data-pid]').first().getAttribute('data-pid');
   const sel=await p.evaluate(pid=>{
     const el=document.querySelector('#reader-body p[data-pid="'+pid+'"]');
     const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,{acceptNode(n){return n.parentElement?.closest('button')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}});
     let n;while((n=w.nextNode())){if(n.nodeValue.trim().length>=12){const r=document.createRange();r.setStart(n,0);r.setEnd(n,Math.min(12,n.nodeValue.length));const s=window.getSelection();s.removeAllRanges();s.addRange(r);document.dispatchEvent(new Event('selectionchange'));return r.toString();}}return null;
   },pid);
   if(!sel)throw new Error('could not create selection');
   await p.waitForSelector('#sel-bar.open',{timeout:3000});
   const pending=await p.evaluate(()=>State.pendingSel);
   if(!pending||pending.whole||pending.pid!==pid||pending.end<=pending.start)throw new Error('range selection not captured '+JSON.stringify(pending));
   await p.click('#sel-action-highlight');await p.waitForSelector('#hl-picker.open');await p.locator('#hlp-swatches .hlp-swatch').nth(1).click();
   await p.waitForFunction(pid=>(State.highlights.get(pid)||[]).some(h=>h.range),pid);
   const before=await p.evaluate(pid=>({records:State.highlights.get(pid),marks:document.querySelectorAll('#reader-body p[data-pid="'+pid+'"] mark').length}),pid);
   if(!before.records.some(h=>h.range)||before.marks<1)throw new Error('range highlight not rendered '+JSON.stringify(before));
   await p.reload({waitUntil:'domcontentloaded',timeout:60000});await ready(p);
   const after=await p.evaluate(pid=>({records:State.highlights.get(pid)||[],readerResumed:document.getElementById('screen-reader').classList.contains('active'),marks:document.querySelectorAll('#reader-body p[data-pid="'+pid+'"] mark').length}),pid);
   if(!after.records.some(h=>h.range))throw new Error('range highlight not durable '+JSON.stringify(after));
   const bad=qualifying(errs);if(bad.length)throw new Error('range errors '+JSON.stringify(bad));
   out.rangeHighlight={pid,selected:sel,pending,before,after,errors:errs};await c.close();
 }

 // C. Actual backup-file preview + Replace restore must remove later state, not merge.
 {
   const c=await b.newContext({viewport:{width:390,height:844},colorScheme:'dark'});
   await c.addInitScript(()=>{localStorage.setItem('mjv_onboarded','1');localStorage.setItem('mjv_theme','dark')});
   const p=await c.newPage(),errs=[];await errorsOn(p,errs);await p.goto(BASE,{waitUntil:'domcontentloaded',timeout:60000});await ready(p);await core(p,'restore');
   // Build source state A.
   await p.click('.cal-cell[data-day="1"]');await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
   const sourceUnit=await p.evaluate(()=>currentUnit().unit_id);await p.click('#btn-complete');await p.click('#btn-activate');
   await p.click('#btn-textsize');await p.click('#textsize-panel .textsize-option[data-text-level="xlarge"]');
   let para=p.locator('#reader-body p[data-pid]').first();await para.hover();await p.locator('#reader-body .para-note-btn').first().click();await p.fill('#note-textarea','RESTORE_SOURCE_NOTE');await p.click('#note-modal .modal-btn-save');await p.waitForFunction(()=>Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE'));
   const backupJson=await p.evaluate(()=>JSON.stringify(App.buildBackupEnvelope(new Date().toISOString())));
   const source=await p.evaluate(()=>({read:[...State.read],activeDay:State.activeDay,textSize:State.textSize,sourceNote:Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE')}));
   // Mutate to state B after backup.
   await p.evaluate(()=>App.startNewCycle());await p.waitForSelector('#cycle-reset-modal.open');await p.click('#cycle-reset-confirm');await p.waitForFunction(()=>State.read.size===0&&State.activeDay===null);
   await p.evaluate(()=>App.openUnit('VM_DV.D02'));await p.waitForFunction(()=>document.getElementById('screen-reader').classList.contains('active'));
   await p.click('#btn-complete');para=p.locator('#reader-body p[data-pid]').first();await para.hover();await p.locator('#reader-body .para-note-btn').first().click();await p.fill('#note-textarea','RESTORE_LATER_NOTE');await p.click('#note-modal .modal-btn-save');await p.waitForFunction(()=>Object.values(State.notes).some(n=>n.text==='RESTORE_LATER_NOTE'));
   await p.evaluate(()=>App.applyTextSize('normal'));
   const later=await p.evaluate(()=>({read:[...State.read],textSize:State.textSize,sourceNote:Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE'),laterNote:Object.values(State.notes).some(n=>n.text==='RESTORE_LATER_NOTE')}));
   if(!later.laterNote)throw new Error('later mutation missing');
   // Upload exact backup file through the actual file input and confirm Replace.
   await p.locator('#backup-file-input').setInputFiles({name:'reaudit-backup.json',mimeType:'application/json',buffer:Buffer.from(backupJson)});
   await p.waitForSelector('#restore-modal.open');
   const preview=await p.locator('#restore-summary').innerText();if(!/Progression/.test(preview)||!/Notes/.test(preview))throw new Error('restore preview incomplete '+preview);
   await p.click('#restore-confirm-btn');await p.waitForFunction(()=>Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE')&&!Object.values(State.notes).some(n=>n.text==='RESTORE_LATER_NOTE'));
   const restored=await p.evaluate(()=>({read:[...State.read],activeDay:State.activeDay,textSize:State.textSize,sourceNote:Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE'),laterNote:Object.values(State.notes).some(n=>n.text==='RESTORE_LATER_NOTE'),toast:document.getElementById('toast').textContent}));
   if(JSON.stringify(restored.read)!==JSON.stringify(source.read)||restored.activeDay!==source.activeDay||restored.textSize!=='xlarge'||!restored.sourceNote||restored.laterNote)throw new Error('replace restore mismatch '+JSON.stringify({source,later,restored}));
   await p.reload({waitUntil:'domcontentloaded',timeout:60000});await ready(p);
   const reopened=await p.evaluate(()=>({read:[...State.read],activeDay:State.activeDay,textSize:State.textSize,sourceNote:Object.values(State.notes).some(n=>n.text==='RESTORE_SOURCE_NOTE'),laterNote:Object.values(State.notes).some(n=>n.text==='RESTORE_LATER_NOTE')}));
   if(JSON.stringify(reopened.read)!==JSON.stringify(source.read)||reopened.activeDay!==source.activeDay||reopened.textSize!=='xlarge'||!reopened.sourceNote||reopened.laterNote)throw new Error('restored state not durable '+JSON.stringify(reopened));
   const bad=qualifying(errs);if(bad.length)throw new Error('restore errors '+JSON.stringify(bad));
   out.restore={sourceUnit,source,later,preview,restored,reopened,errors:errs};await c.close();
 }

 await b.close();out.status='PASS';fs.writeFileSync('MJV_v48_B3_FINAL_FRESH_BLIND_2026-10-04.json',JSON.stringify(out,null,2));console.log('MJV_V48_B3_FINAL_FRESH_BLIND_PASS');
})().catch(e=>{console.error(e);process.exit(2)});