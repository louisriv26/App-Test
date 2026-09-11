#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VERSION=sys.argv[3] if len(sys.argv)>3 else 'v101.122'

STUB="""() => { const mem=new Map(); const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}}; Object.defineProperty(window,'localStorage',{value:ls,configurable:true}); Object.defineProperty(window,'__qaMem',{value:mem,configurable:true}); }"""

async def make_page(browser):
    ctx=await browser.new_context(viewport={'width':1200,'height':900},user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36')
    page=await ctx.new_page(); await page.evaluate(STUB); await page.set_content(HTML,wait_until='domcontentloaded'); await page.wait_for_timeout(80)
    return ctx,page

def row(rows,sid,ok,detail): rows.append({'case':sid,'status':'PASS' if ok else 'FAIL','detail':detail})

async def main():
 rows=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  # S01 Hour23 unchanged
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set();openHour(23,false);const t=document.getElementById('content').innerText;return {actions:['Réflexion et pratique','Approfondir','Revenir au début','Prier la 24e Heure'].map(x=>[x,t.includes(x)]),progress:t.includes('Voir ma progression'),review:t.includes('Revoir les Heures méditées')}}""")
  row(rows,'S01',all(x[1] for x in d['actions']) and not d['progress'] and not d['review'],d); await ctx.close()
  # S02 0/24
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set();openHour(24,false);const panel=document.getElementById('hour24CyclePanelHost').innerText;return {panel,restart:panel.includes('Recommencer')}}""")
  row(rows,'S02','VOTRE PARCOURS' in d['panel'] and '0/24' in d['panel'] and not d['restart'],d);await ctx.close()
  # S03 22/24
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:22},(_,i)=>i+1));openHour(24,false);const panel=document.getElementById('hour24CyclePanelHost').innerText;return {panel,restart:panel.includes('Recommencer')}}""")
  row(rows,'S03','22/24' in d['panel'] and 'VOTRE PARCOURS' in d['panel'] and not d['restart'],d);await ctx.close()
  # S04 23/24 hour24 missing -> meditee -> complete
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));state.meditationLog=[];openHour(24,false);const before=document.getElementById('hour24CyclePanelHost').innerText;markMeditee(24);const after=document.getElementById('hour24CyclePanelHost').innerText;return {before,after,count:state.readHours.size,has24:state.readHours.has(24)}}""")
  row(rows,'S04','23/24' in d['before'] and '24/24' in d['after'] and 'ACCOMPLI' in d['after'] and d['count']==24 and d['has24'],d);await ctx.close()
  # S05 complete -> undo 24 -> incomplete
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));state.meditationLog=[];openHour(24,false);const before=document.getElementById('hour24CyclePanelHost').innerText;markMeditee(24);const after=document.getElementById('hour24CyclePanelHost').innerText;return {before,after,count:state.readHours.size,has24:state.readHours.has(24)}}""")
  row(rows,'S05','24/24' in d['before'] and 'ACCOMPLI' in d['before'] and '23/24' in d['after'] and 'Recommencer' not in d['after'] and d['count']==23 and not d['has24'],d);await ctx.close()
  # S06 hour24 marked but another hour missing
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {const a=Array.from({length:24},(_,i)=>i+1).filter(n=>n!==7);state.readHours=new Set(a);openHour(24,false);const panel=document.getElementById('hour24CyclePanelHost').innerText;return {panel,count:state.readHours.size,has24:state.readHours.has(24),complete:getProgressSnapshot().complete}}""")
  row(rows,'S06',d['count']==23 and d['has24'] and not d['complete'] and '23/24' in d['panel'] and 'Recommencer' not in d['panel'],d);await ctx.close()
  # S07 complete restart cancel no mutation
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));state.lastParas={24:'PASSION24.HOUR.24.P001'};state.hourTabs={24:'linked'};state.meditationLog=[{date:'2026-08-27',hour:24}];state.notes={n1:{text:'keep'}};state.textHighlights={x:[{id:'h',start_offset:0,end_offset:1,color:'yellow'}]};state.themePreference='dark';state.lastHour=24;const before=JSON.stringify(buildPersonalSnapshotFromState());window.confirm=()=>false;const ret=restartTwentyFourHours({requireComplete:true,destination:'hour1'});const after=JSON.stringify(buildPersonalSnapshotFromState());return {ret,same:before===after,count:state.readHours.size,lastHour:state.lastHour,view:state.view}}""")
  row(rows,'S07',d['ret'] is False and d['same'] and d['count']==24 and d['lastHour']==24,d);await ctx.close()
  # S08 complete restart confirm reset + direct hour1 + protected personal fields
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));state.lastParas={24:'PASSION24.HOUR.24.P001'};state.hourTabs={24:'linked'};state.meditationLog=[{date:'2026-08-27',hour:24}];state.notes={n1:{text:'keep'}};state.textHighlights={x:[{id:'h',start_offset:0,end_offset:1,color:'yellow'}]};state.libraryMarks={m1:{id:'m1'}};state.themePreference='dark';state.lastHour=24;const protectedBefore=JSON.stringify({notes:state.notes,textHighlights:state.textHighlights,libraryMarks:state.libraryMarks,themePreference:state.themePreference});window.confirm=()=>true;const ret=restartTwentyFourHours({requireComplete:true,destination:'hour1'});const protectedAfter=JSON.stringify({notes:state.notes,textHighlights:state.textHighlights,libraryMarks:state.libraryMarks,themePreference:state.themePreference});return {ret,count:state.readHours.size,lastParas:Object.keys(state.lastParas).length,hourTabs:Object.keys(state.hourTabs).length,log:state.meditationLog.length,currentHour:state.currentHour,lastHour:state.lastHour,view:state.view,protectedSame:protectedBefore===protectedAfter}}""")
  row(rows,'S08',d['ret'] and d['count']==0 and d['lastParas']==0 and d['hourTabs']==0 and d['log']==0 and d['currentHour']==1 and int(d['lastHour'])==1 and d['view']=='reader' and d['protectedSame'],d);await ctx.close()
  # S09 forced complete-reset call on incomplete state
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));state.lastParas={24:'X'};state.notes={n:{text:'keep'}};const before=JSON.stringify(buildPersonalSnapshotFromState());window.confirm=()=>true;const ret=restartTwentyFourHours({requireComplete:true,destination:'hour1'});const after=JSON.stringify(buildPersonalSnapshotFromState());return {ret,same:before===after,count:state.readHours.size}}""")
  row(rows,'S09',d['ret'] is False and d['same'] and d['count']==23,d);await ctx.close()
  # S10 reflection action routes to reflection tab
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {openHour(24,false);goToHourTab('reflections','reflectionsContent');return {tab:state.activeTab,display:getComputedStyle(document.getElementById('reflectionsContent')).display,hash:location.hash}}""")
  row(rows,'S10',d['tab']=='reflections' and d['display']!='none',d);await ctx.close()
  # S11 approfondir action routes to linked
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {openHour(24,false);goToHourTab('linked','linkedTextsContent');return {tab:state.activeTab,display:getComputedStyle(document.getElementById('linkedTextsContent')).display}}""")
  row(rows,'S11',d['tab']=='linked' and d['display']!='none',d);await ctx.close()
  # S12 return to beginning keeps same hour and reaches top
  ctx,p=await make_page(browser)
  await p.evaluate("""() => {openHour(24,false);const c=document.getElementById('content');c.scrollTop=Math.max(300,c.scrollHeight-400);scrollReaderToTop();}"""); await p.wait_for_timeout(450)
  d=await p.evaluate("""() => ({hour:state.currentHour,view:state.view,scroll:document.getElementById('content').scrollTop})""")
  row(rows,'S12',d['hour']==24 and d['view']=='reader' and d['scroll']<=5,d);await ctx.close()
  # S13 Progress screen persistent Accueil works
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {showProgressView(false);const home=[...document.querySelectorAll('.bottom-nav button')].find(x=>/Accueil/.test(x.innerText||x.getAttribute('aria-label')||''));if(home)home.click();return {home:!!home,view:state.view}}""")
  row(rows,'S13',d['home'] and d['view']=='home',d);await ctx.close()
  # S14 Completed screen persistent Accueil works
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {showCompletedHoursView(false);const home=[...document.querySelectorAll('.bottom-nav button')].find(x=>/Accueil/.test(x.innerText||x.getAttribute('aria-label')||''));if(home)home.click();return {home:!!home,view:state.view}}""")
  row(rows,'S14',d['home'] and d['view']=='home',d);await ctx.close()
  # S15 ordinary Meditee persists through loadState from canonical storage
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set();state.meditationLog=[];openHour(6,false);markMeditee(6);const raw=localStorage.getItem(PERSONAL_SNAPSHOT_KEY);state.readHours=new Set();state.meditationLog=[];loadState();return {raw:!!raw,has6:state.readHours.has(6),count:state.readHours.size,log:state.meditationLog.some(x=>x.hour===6)}}""")
  row(rows,'S15',d['raw'] and d['has6'] and d['count']==1 and d['log'],d);await ctx.close()
  # S16 completed reset persists and resume becomes Hour1 consistently
  ctx,p=await make_page(browser)
  d=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));state.lastParas={24:'X'};state.hourTabs={24:'linked'};state.meditationLog=[{date:'2026-08-27',hour:24}];state.lastHour=24;window.confirm=()=>true;const ret=restartTwentyFourHours({requireComplete:true,destination:'hour1'});const raw=localStorage.getItem(PERSONAL_SNAPSHOT_KEY);const snap=raw?JSON.parse(raw):null;state.readHours=new Set([2]);state.lastHour=2;loadState();return {ret,raw:!!raw,snapRead:snap&&snap.readHours,snapLast:snap&&snap.lastHour,loadedCount:state.readHours.size,loadedLast:state.lastHour}}""")
  row(rows,'S16',d['ret'] and d['raw'] and d['snapRead']==[] and str(d['snapLast'])=='1' and d['loadedCount']==0 and int(d['loadedLast'])==1,d);await ctx.close()
  await browser.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.write_text(json.dumps({'schema':'L24H_V101122_HOUR24_STATE_TRANSITION_MATRIX_V1','version':VERSION,'browser':'system Chromium via Playwright content injection','real_device_limitation':'browser emulation only; physical-device gates not claimed','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary)); raise SystemExit(0 if summary['fail']==0 and summary['total']==16 else 2)
asyncio.run(main())
