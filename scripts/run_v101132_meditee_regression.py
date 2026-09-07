#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VERSION='v101.132'
PROFILES=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_portrait',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_landscape',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
STUB="""() => { const mem=new Map(); const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}}; Object.defineProperty(window,'localStorage',{value:ls,configurable:true}); Object.defineProperty(window,'__qaMem',{value:mem,configurable:true}); }"""
async def new_page(browser,w=1200,h=900,ua=PROFILES[3][3]):
 ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua,color_scheme='light')
 p=await ctx.new_page();await p.evaluate(STUB);errs=[];p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded');await p.wait_for_timeout(70);return ctx,p,errs
async def main():
 rows=[]
 def add(group,case,ok,detail=None):rows.append({'group':group,'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  print('START browser',flush=True)
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  print('GROUP dual',flush=True)
  # Exhaustive 24-Hour dual-control state synchronization.
  ctx,p,errs=await new_page(b)
  for n in range(1,25):
   d=await p.evaluate('''(n)=>{state.readHours=new Set();state.meditationLog=[];openHour(n,false);const top=document.querySelector(`[data-meditee-role="recovery"][data-meditee-action-hour="${n}"]`),bot=document.querySelector(`[data-meditee-role="primary-end"][data-meditee-action-hour="${n}"]`);function snap(){return{has:state.readHours.has(n),topText:top&&top.innerText.trim(),botText:bot&&bot.innerText.trim(),topAria:top&&top.getAttribute('aria-pressed'),botAria:bot&&bot.getAttribute('aria-pressed'),topDone:top&&top.classList.contains('done'),botDone:bot&&bot.classList.contains('done'),barDone:!!document.querySelector(`[data-meditee-bar-hour="${n}"].done`)}}const a=snap();top.click();const b=snap();bot.click();const c=snap();bot.click();const d=snap();top.click();const e=snap();return{a,b,c,d,e,topExists:!!top,botExists:!!bot}}''',n)
   add('dual_control',f'H{n:02d}_controls_exist',d['topExists'] and d['botExists'],d)
   a=d['a'];add('dual_control',f'H{n:02d}_initial_unread',not a['has'] and a['topAria']=='false' and a['botAria']=='false' and not a['topDone'] and not a['botDone'],a)
   x=d['b'];add('dual_control',f'H{n:02d}_top_marks_both',x['has'] and x['topAria']=='true' and x['botAria']=='true' and x['topDone'] and x['botDone'] and x['barDone'],x)
   x=d['c'];add('dual_control',f'H{n:02d}_bottom_unmarks_both',not x['has'] and x['topAria']=='false' and x['botAria']=='false' and not x['topDone'] and not x['botDone'],x)
   x=d['d'];add('dual_control',f'H{n:02d}_bottom_marks_both',x['has'] and x['topAria']=='true' and x['botAria']=='true',x)
   x=d['e'];add('dual_control',f'H{n:02d}_top_unmarks_both',not x['has'] and x['topAria']=='false' and x['botAria']=='false',x)
  add('dual_control','no_page_errors',not errs,errs);await ctx.close()

  print('GROUP persistence',flush=True)
  # Persistence success, hard rollback, durability uncertainty.
  ctx,p,errs=await new_page(b)
  suc=await p.evaluate('''()=>{state.readHours=new Set();state.meditationLog=[];openHour(6,false);document.querySelector('[data-meditee-role="recovery"]').click();const raw=localStorage.getItem(PERSONAL_SNAPSHOT_KEY);state.readHours=new Set();state.meditationLog=[];loadState();openHour(6,false);const top=document.querySelector('[data-meditee-role="recovery"]'),bot=document.querySelector('[data-meditee-role="primary-end"]');return{raw:!!raw,has:state.readHours.has(6),top:top.getAttribute('aria-pressed'),bot:bot.getAttribute('aria-pressed')}}''')
  add('persistence','success_reload',suc['raw'] and suc['has'] and suc['top']=='true' and suc['bot']=='true',suc)
  hard=await p.evaluate('''()=>{state.readHours=new Set();state.meditationLog=[];openHour(7,false);const originalSave=saveState;saveState=()=>({ok:false,error:new Error('qa hard failure'),durabilityUncertain:false});document.querySelector('[data-meditee-role="recovery"]').click();saveState=originalSave;const top=document.querySelector('[data-meditee-role="recovery"]'),bot=document.querySelector('[data-meditee-role="primary-end"]');return{has:state.readHours.has(7),top:top.getAttribute('aria-pressed'),bot:bot.getAttribute('aria-pressed')}}''')
  add('persistence','hard_failure_rolls_back_and_ui_truth',not hard['has'] and hard['top']=='false' and hard['bot']=='false',hard)
  unc=await p.evaluate('''()=>{state.readHours=new Set();state.meditationLog=[];openHour(8,false);const originalSave=saveState;saveState=()=>({ok:false,error:new Error('qa uncertain'),durabilityUncertain:true});document.querySelector('[data-meditee-role="recovery"]').click();saveState=originalSave;const top=document.querySelector('[data-meditee-role="recovery"]'),bot=document.querySelector('[data-meditee-role="primary-end"]');return{has:state.readHours.has(8),top:top.getAttribute('aria-pressed'),bot:bot.getAttribute('aria-pressed')}}''')
  add('persistence','uncertain_keeps_in_session_truth',unc['has'] and unc['top']=='true' and unc['bot']=='true',unc)
  add('persistence','no_page_errors',not errs,errs);await ctx.close()

  print('GROUP scroll',flush=True)
  # No full-reader rerender, focus and scroll preservation.
  ctx,p,errs=await new_page(b)
  top=await p.evaluate('''()=>{state.readHours=new Set();openHour(9,false);const original=renderReader;window.__qaRenderCount=0;renderReader=function(...a){window.__qaRenderCount++;return original(...a)};const c=document.getElementById('content');c.scrollTop=0;const btn=document.querySelector('[data-meditee-role="recovery"]');btn.focus();const before=c.scrollTop;btn.click();return{before,after:c.scrollTop,render:window.__qaRenderCount,focused:document.activeElement===btn,has:state.readHours.has(9)}}''')
  add('scroll_focus','top_no_rerender',top['render']==0,top);add('scroll_focus','top_focus_preserved',top['focused'],top);add('scroll_focus','top_scroll_preserved',abs(top['after']-top['before'])<=1,top)
  bottom=await p.evaluate('''()=>{state.readHours=new Set();openHour(10,false);const original=renderReader;window.__qaRenderCount=0;renderReader=function(...a){window.__qaRenderCount++;return original(...a)};const c=document.getElementById('content');c.scrollTop=c.scrollHeight-c.clientHeight;const btn=document.querySelector('[data-meditee-role="primary-end"]');btn.focus();const before=c.scrollTop;btn.click();return{before,after:c.scrollTop,render:window.__qaRenderCount,focused:document.activeElement===btn,has:state.readHours.has(10)}}''')
  add('scroll_focus','bottom_no_rerender',bottom['render']==0,bottom);add('scroll_focus','bottom_focus_preserved',bottom['focused'],bottom);add('scroll_focus','bottom_scroll_preserved',abs(bottom['after']-bottom['before'])<=1,bottom)
  add('scroll_focus','no_page_errors',not errs,errs);await ctx.close()

  print('GROUP resume',flush=True)
  # Resume path: saved paragraph remains the authority and toggle does not alter it.
  ctx,p,errs=await new_page(b)
  res=await p.evaluate('''async()=>{state.readHours=new Set();openHour(11,false);const paras=[...document.querySelectorAll('#meditationContent .para-block[id]')];const target=paras[Math.max(1,Math.floor(paras.length*0.65))];state.lastParas[11]=target.id;saveState({silent:true});const saved=state.lastParas[11];openHour(12,false);openHour(11,false,{resume:true});await new Promise(r=>setTimeout(r,180));const c=document.getElementById('content'),el=document.getElementById(saved),cr=c.getBoundingClientRect(),er=el.getBoundingClientRect();const before=state.lastParas[11];markMeditee(11);return{saved,before,after:state.lastParas[11],near:er.bottom>=cr.top-10&&er.top<=cr.bottom+10,scroll:c.scrollTop,has:state.readHours.has(11)}}''')
  add('resume','saved_para_restored',res['near'],res);add('resume','toggle_does_not_change_lastParas',res['before']==res['after'],res);add('resume','toggle_state_changed',res['has'],res);add('resume','no_page_errors',not errs,errs);await ctx.close()

  print('GROUP h24',flush=True)
  # Hour 24 truth table including recovery action.
  ctx,p,errs=await new_page(b)
  h24a=await p.evaluate('''()=>{state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));openHour(24,false);const before=getProgressSnapshot();document.querySelector('[data-meditee-role="recovery"]').click();const after=getProgressSnapshot();return{before,after,panel:document.getElementById('hour24CyclePanelHost').innerText,top:document.querySelector('[data-meditee-role="recovery"]').getAttribute('aria-pressed'),bot:document.querySelector('[data-meditee-role="primary-end"]').getAttribute('aria-pressed')}}''')
  add('hour24','23_to_24_via_top',h24a['before']['count']==23 and not h24a['before']['complete'] and h24a['after']['count']==24 and h24a['after']['complete'] and 'ACCOMPLI' in h24a['panel'] and h24a['top']=='true' and h24a['bot']=='true',h24a)
  h24b=await p.evaluate('''()=>{document.querySelector('[data-meditee-role="recovery"]').click();const x=getProgressSnapshot();return{x,panel:document.getElementById('hour24CyclePanelHost').innerText,top:document.querySelector('[data-meditee-role="recovery"]').getAttribute('aria-pressed'),bot:document.querySelector('[data-meditee-role="primary-end"]').getAttribute('aria-pressed')}}''')
  add('hour24','24_to_23_via_top',h24b['x']['count']==23 and not h24b['x']['complete'] and 'VOTRE PARCOURS' in h24b['panel'] and 'Recommencer' not in h24b['panel'] and h24b['top']=='false' and h24b['bot']=='false',h24b)
  h24c=await p.evaluate('''()=>{state.readHours=new Set([...Array.from({length:22},(_,i)=>i+1),24]);openHour(24,false);const x=getProgressSnapshot();return{x,panel:document.getElementById('hour24CyclePanelHost').innerText}}''')
  add('hour24','h24_marked_other_hour_missing_still_incomplete',h24c['x']['count']==23 and not h24c['x']['complete'] and 'VOTRE PARCOURS' in h24c['panel'] and 'Recommencer' not in h24c['panel'],h24c)
  add('hour24','no_page_errors',not errs,errs);await ctx.close()

  await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101128_MEDITEE_CORE_MATRIX_V1','version':VERSION,'real_device_limitation':'Chromium/browser profile evidence only; physical iPhone/iPad/Samsung and VoiceOver/TalkBack remain open','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary));
 if summary['fail']:
  for r in rows:
   if r['status']=='FAIL':print('FAIL',r['group'],r['case'],r['detail'])
  raise SystemExit(2)
asyncio.run(main())
