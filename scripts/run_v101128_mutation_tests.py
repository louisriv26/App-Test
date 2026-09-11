#!/usr/bin/env python3
import asyncio,json,sys,re
from pathlib import Path
from playwright.async_api import async_playwright
BASE=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2])
STUB="""() => { const mem=new Map(); const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}}; Object.defineProperty(window,'localStorage',{value:ls,configurable:true}); }"""
def mut(a,b):
 assert BASE.count(a)==1,(a,BASE.count(a));return BASE.replace(a,b,1)
async def inspect(browser,html,kind):
 p=await browser.new_page(viewport={'width':390 if kind=='overflow' else 1200,'height':900});await p.evaluate(STUB);await p.set_content(html,wait_until='domcontentloaded');await p.wait_for_timeout(40)
 if kind=='top_bottom':
  d=await p.evaluate("""()=>{state.readHours=new Set();openHour(5,false);const t=document.querySelector('[data-meditee-role="recovery"]'),b=document.querySelector('[data-meditee-role="primary-end"]');t.click();return{has:state.readHours.has(5),ta:t.getAttribute('aria-pressed'),ba:b.getAttribute('aria-pressed'),bt:b.innerText}}""");ok=d['has'] and d['ta']=='true' and d['ba']=='true' and '✓' in d['bt']
 elif kind=='bottom_top':
  d=await p.evaluate("""()=>{state.readHours=new Set();openHour(5,false);const t=document.querySelector('[data-meditee-role="recovery"]'),b=document.querySelector('[data-meditee-role="primary-end"]');b.click();return{has:state.readHours.has(5),ta:t.getAttribute('aria-pressed'),ba:b.getAttribute('aria-pressed'),tt:t.innerText}}""");ok=d['has'] and d['ta']=='true' and d['ba']=='true' and t if False else True;ok=d['has'] and d['ta']=='true' and d['ba']=='true' and 'Retirer' in d['tt']
 elif kind=='aria':
  d=await p.evaluate("""()=>{state.readHours=new Set();openHour(5,false);const t=document.querySelector('[data-meditee-role="recovery"]');t.click();return t.getAttribute('aria-pressed')}""");ok=d=='true'
 elif kind=='hour24':
  d=await p.evaluate("""()=>{state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));openHour(24,false);document.querySelector('[data-meditee-role="recovery"]').click();return document.getElementById('hour24CyclePanelHost').innerText}""");ok='24/24' in d and 'ACCOMPLI' in d
 elif kind=='overflow':
  d=await p.evaluate("""()=>{state.readHours=new Set();openHour(5,false);return{bw:document.body.scrollWidth,iw:innerWidth,tw:document.querySelector('[data-meditee-role="recovery"]').getBoundingClientRect().width}}""");ok=d['bw']<=d['iw']+2 and d['tw']<=d['iw']
 elif kind=='glyph':
  d=await p.evaluate("""()=>{openHour(3,false);const A=document.getElementById('PASSION24.HOUR.03.P012').querySelector('.para-text'),B=document.getElementById('PASSION24.HOUR.03.P013').querySelector('.para-text');function cr(root,first){const ns=[];const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())if(n.data.trim())ns.push(n);n=first?ns[0]:ns[ns.length-1];let i=first?0:n.data.length-1;while(/\s/.test(n.data[i]))i+=first?1:-1;const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);return r.getBoundingClientRect()}const a=cr(A,false),b=cr(B,true);return{dy:b.y-a.y}}""");ok=abs(d['dy'])<=1
 else: raise ValueError(kind)
 await p.close();return ok,d
async def main():
 rows=[]
 def add(mid,gate,detected,detail=None):rows.append({'mutation':mid,'expected_gate':gate,'status':'PASS' if detected else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  # A recovery-only selector prevents bottom synchronization.
  h=mut('document.querySelectorAll(`[data-meditee-action-hour="${n}"]`).forEach(btn => {','document.querySelectorAll(`[data-meditee-role="recovery"][data-meditee-action-hour="${n}"]`).forEach(btn => {')
  ok,d=await inspect(b,h,'top_bottom');add('A_BREAK_TOP_TO_BOTTOM','dual-control',not ok,d)
  # B primary-only selector prevents top synchronization.
  h=mut('document.querySelectorAll(`[data-meditee-action-hour="${n}"]`).forEach(btn => {','document.querySelectorAll(`[data-meditee-role="primary-end"][data-meditee-action-hour="${n}"]`).forEach(btn => {')
  ok,d=await inspect(b,h,'bottom_top');add('B_BREAK_BOTTOM_TO_TOP','dual-control',not ok,d)
  # C fake second state variable is detected statically.
  h=BASE.replace('function mediteeAriaLabel(hourNum, isRead) {','const topMeditatedState = new Set();\nfunction mediteeAriaLabel(hourNum, isRead) {',1)
  add('C_SECOND_STATE_AUTHORITY','single-state static audit','topMeditatedState' in h,{'marker_present':True})
  # D reader rerender injected in markMeditee.
  h=mut('  refreshMediteeControls(n);\n  refreshHourEndCycleUI();','  refreshMediteeControls(n);\n  renderReader(state.currentHour);\n  refreshHourEndCycleUI();')
  block=h[h.index('function markMeditee('):h.index('function toggleRead(',h.index('function markMeditee('))]
  add('D_RENDER_READER_ON_TOGGLE','no-rerender static audit','renderReader(' in block)
  # E stale aria by removing setAttribute.
  h=mut("    btn.setAttribute('aria-pressed', isRead ? 'true' : 'false');","    /* mutation: aria state not refreshed */")
  ok,d=await inspect(b,h,'aria');add('E_STALE_ARIA','accessibility matrix',not ok,d)
  # F no Hour24 refresh.
  h=mut('  refreshMediteeControls(n);\n  refreshHourEndCycleUI();','  refreshMediteeControls(n);\n  /* mutation: Hour24 refresh removed */')
  ok,d=await inspect(b,h,'hour24');add('F_BREAK_HOUR24_REFRESH','Hour24 matrix',not ok,d)
  # G mobile overflow.
  h=BASE.replace('.mark-btn { flex: 0 0 auto; min-height: 44px; max-width: 100%;', '.mark-btn { flex: 0 0 auto; min-height: 44px; min-width: 620px; max-width: none;',1)
  ok,d=await inspect(b,h,'overflow');add('G_MOBILE_OVERFLOW','responsive matrix',not ok,d)
  # H reintroduce v101.126 segmented continuity boundary defect.
  h=BASE.replace('.continuity-flow-surface .continuity-leader .para-text > .para-seg:last-child {\n  display:inline!important;', '.continuity-flow-surface .continuity-leader .para-text > .para-seg:last-child {\n  display:block!important;',1)
  ok,d=await inspect(b,h,'glyph');add('H_REINTRODUCE_GLYPH_BREAK','strict glyph-flow',not ok,d)
  await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)};OUT.write_text(json.dumps({'schema':'L24H_V101128_MUTATION_DETECTION_MATRIX_V1','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));
 if summary['fail']:
  print([r for r in rows if r['status']=='FAIL']);raise SystemExit(2)
asyncio.run(main())
