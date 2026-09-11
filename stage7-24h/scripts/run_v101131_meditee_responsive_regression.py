#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VERSION='v101.131'
PROFILES=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_portrait',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_landscape',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
STUB="""() => { const mem=new Map(); const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}}; Object.defineProperty(window,'localStorage',{value:ls,configurable:true}); }"""
async def main():
 rows=[]
 def add(profile,case,ok,detail=None):rows.append({'profile':profile,'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in PROFILES:
   ctx=await b.new_context(viewport={'width':w,'height':h},user_agent=ua,color_scheme='light');p=await ctx.new_page();await p.evaluate(STUB);errs=[];p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded');await p.wait_for_timeout(60)
   for scheme in ['light','dark']:
    for font in ['normal','large']:
     for isread in [False,True]:
      d=await p.evaluate('''([read,scheme,font])=>{state.themePreference=scheme;applyTheme();state.fontLevel=font;state.fontSize=fontIndexFromLevel(font,1);applyFontSize();state.readHours=read?new Set([5]):new Set();openHour(5,false);const top=document.querySelector('[data-meditee-role="recovery"]'),bot=document.querySelector('[data-meditee-role="primary-end"]'),bar=document.querySelector('.mark-bar'),c=document.getElementById('content');const br=x=>x.getBoundingClientRect();const ids=[...document.querySelectorAll('[id]')].map(x=>x.id).filter(Boolean),dups=ids.filter((x,i)=>ids.indexOf(x)!==i);const pos=getComputedStyle(bar).position;return{v:APP_VERSION,theme:document.documentElement.getAttribute('data-theme'),font:state.fontLevel,topText:top.innerText.trim(),botText:bot.innerText.trim(),topAria:top.getAttribute('aria-pressed'),botAria:bot.getAttribute('aria-pressed'),topLabel:top.getAttribute('aria-label'),botLabel:bot.getAttribute('aria-label'),topW:br(top).width,topH:br(top).height,botW:br(bot).width,botH:br(bot).height,barL:br(bar).left,barR:br(bar).right,inner:innerWidth,bodyW:document.body.scrollWidth,contentW:c.scrollWidth,contentClient:c.clientWidth,pos,dups}}''',[isread,scheme,font])
      key=f'{scheme}_{font}_{"read" if isread else "unread"}'
      add(label,key+'_identity',d['v']==VERSION and d['theme']==scheme and d['font']==font,d)
      add(label,key+'_no_overflow',d['bodyW']<=d['inner']+2 and d['contentW']<=d['contentClient']+2 and d['barL']>=-2 and d['barR']<=d['inner']+2,d)
      add(label,key+'_touch_targets',d['topH']>=44 and d['botH']>=40,d)
      add(label,key+'_aria_truth',d['topAria']==('true' if isread else 'false') and d['botAria']==('true' if isread else 'false') and bool(d['topLabel']) and bool(d['botLabel']),d)
      add(label,key+'_normal_flow',d['pos'] not in ('fixed','sticky'),d['pos'])
      add(label,key+'_no_duplicate_ids',len(d['dups'])==0,d['dups'])
   add(label,'no_page_errors',not errs,errs);await ctx.close()
  await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101128_MEDITEE_RESPONSIVE_MATRIX_V1','version':VERSION,'profiles':[x[0] for x in PROFILES],'dimensions':['light/dark','normal/large','read/unread'],'real_device_limitation':'Browser-profile evidence only; physical-device and screen-reader gates remain open','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary));
 if summary['fail']:
  for r in rows:
   if r['status']=='FAIL': print('FAIL',r)
  raise SystemExit(2)
asyncio.run(main())
