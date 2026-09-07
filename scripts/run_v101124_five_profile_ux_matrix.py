#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2]);VERSION=sys.argv[3] if len(sys.argv)>3 else 'v101.124'
profiles=[
 ('phone',390,844,'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_portrait',820,1180,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('ipad_landscape',1180,820,'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'),
 ('desktop',1200,900,'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/142.0 Safari/537.36'),
 ('samsung',412,915,'Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 Chrome/142.0 Mobile Safari/537.36 SamsungBrowser/28.0')]
async def main():
 results=[]
 def add(p,n,o,d=''):results.append({'profile':p,'check':n,'status':'PASS' if o else 'FAIL','detail':d})
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h,ua in profiles:
   ctx=await browser.new_context(viewport={'width':w,'height':h},user_agent=ua,color_scheme='light')
   page=await ctx.new_page();await page.evaluate("""() => {const mem=new Map();const ls={getItem:k=>mem.has(String(k))?mem.get(String(k)):null,setItem:(k,v)=>mem.set(String(k),String(v)),removeItem:k=>mem.delete(String(k)),clear:()=>mem.clear(),key:i=>Array.from(mem.keys())[i]||null,get length(){return mem.size}};Object.defineProperty(window,'localStorage',{value:ls,configurable:true});}""")
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(80)
   for mode,count in [('incomplete',23),('complete',24)]:
    d=await page.evaluate("""([count]) => {state.readHours=new Set(Array.from({length:count},(_,i)=>i+1));openHour(24,false);const c=document.getElementById('content');const panel=document.getElementById('hour24CyclePanelHost');const hourEnd=document.getElementById('hourEndActions');const nav=document.querySelector('.hour-nav');const bottom=document.querySelector('.bottom-nav');const br=(x)=>x?x.getBoundingClientRect():null;const visibleButtons=[...document.querySelectorAll('#hourEndActions button,#hour24CyclePanelHost button,.hour-nav button')].filter(b=>{const s=getComputedStyle(b);return s.display!=='none'&&s.visibility!=='hidden'});return {version:APP_VERSION,body:document.body.scrollWidth,inner:innerWidth,contentScrollWidth:c.scrollWidth,contentClientWidth:c.clientWidth,panelText:panel?panel.innerText:'',hourEndText:hourEnd?hourEnd.innerText:'',navText:nav?nav.innerText:'',buttons:visibleButtons.map(b=>({text:b.innerText.trim(),w:br(b).width,h:br(b).height,right:br(b).right,left:br(b).left})),bottom:br(bottom),panel:br(panel),content:br(c),dark:document.documentElement.getAttribute('data-theme')}}""",[count])
    add(label,f'{mode}_identity',d['version']==VERSION,d['version'])
    add(label,f'{mode}_no_horizontal_overflow',d['body']<=d['inner']+2 and d['contentScrollWidth']<=d['contentClientWidth']+2,{'body':d['body'],'inner':d['inner'],'contentScroll':d['contentScrollWidth'],'contentClient':d['contentClientWidth']})
    add(label,f'{mode}_hour_actions',all(x in d['hourEndText'] for x in ['Réflexion et pratique','Approfondir','Revenir au début']),d['hourEndText'])
    if mode=='incomplete': add(label,'incomplete_panel_truth','23/24' in d['panelText'] and 'VOTRE PARCOURS' in d['panelText'] and 'Recommencer' not in d['panelText'],d['panelText'])
    else: add(label,'complete_panel_truth','24/24' in d['panelText'] and 'ACCOMPLI' in d['panelText'] and 'Recommencer depuis la 1re Heure' in d['panelText'],d['panelText'])
    add(label,f'{mode}_no_suivante','Suivante' not in d['navText'],d['navText'])
    add(label,f'{mode}_button_geometry',all(b['w']>=40 and b['h']>=40 and b['left']>=-2 and b['right']<=d['inner']+2 for b in d['buttons']),d['buttons'])
   # dark mode complete state
   dd=await page.evaluate("""() => {setThemePreference('dark');state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));openHour(24,false);return {theme:document.documentElement.getAttribute('data-theme'),panel:document.getElementById('hour24CyclePanelHost').innerText,body:document.body.scrollWidth,inner:innerWidth}}""")
   add(label,'dark_mode_terminal',dd['theme']=='dark' and '24/24' in dd['panel'] and dd['body']<=dd['inner']+2,dd)
   add(label,'no_page_errors',not errors,errors)
   await ctx.close()
  await browser.close()
 summary={'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),'total':len(results),'profiles':len(profiles)}
 OUT.write_text(json.dumps({'schema':'L24H_V101124_FIVE_PROFILE_UX_MATRIX_V1','version':VERSION,'browser':'system Chromium via Playwright content injection','physical_device_limitation':'NOT physical-device evidence','summary':summary,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 else 2)
asyncio.run(main())
