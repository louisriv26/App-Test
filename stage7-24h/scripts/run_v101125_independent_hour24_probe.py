#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2]);VER=sys.argv[3] if len(sys.argv)>3 else 'v101.125'
profiles=[('phone',390,844),('ipad_portrait',820,1180),('ipad_landscape',1180,820),('desktop',1200,900),('samsung',412,915)]
async def main():
 rows=[]
 def ck(p,n,o,d=''):rows.append({'profile':p,'check':n,'status':'PASS' if o else 'FAIL','detail':d})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for lab,w,h in profiles:
   c=await b.new_context(viewport={'width':w,'height':h});p=await c.new_page();errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
   await p.evaluate("""() => {const m=new Map();const s={getItem:k=>m.has(String(k))?m.get(String(k)):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(String(k)),clear:()=>m.clear(),key:i=>Array.from(m.keys())[i]||null,get length(){return m.size}};Object.defineProperty(window,'localStorage',{value:s,configurable:true});}""")
   await p.set_content(HTML,wait_until='domcontentloaded');await p.wait_for_timeout(60)
   x=await p.evaluate("""() => {openHour(23,false);const t23=document.getElementById('content').innerText;state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));openHour(24,false);const inc=document.getElementById('content').innerText;state.readHours=new Set(Array.from({length:24},(_,i)=>i+1));refreshHourEndCycleUI();const comp=document.getElementById('content').innerText;const nav=[...document.querySelectorAll('.hour-nav button')].map(x=>x.innerText.trim());return {ver:APP_VERSION,t23,inc,comp,nav,overflow:document.body.scrollWidth<=innerWidth+2}}""")
   ck(lab,'identity',x['ver']==VER,x['ver'])
   ck(lab,'hour23_contract',all(q in x['t23'] for q in ['Réflexion et pratique','Approfondir','Revenir au début','Prier la 24e Heure']) and 'Voir ma progression' not in x['t23'],None)
   ck(lab,'hour24_hour_actions',all(q in x['inc'] for q in ['Réflexion et pratique','Approfondir','Revenir au début']),None)
   ck(lab,'incomplete_truth','23/24' in x['inc'] and 'VOTRE PARCOURS' in x['inc'] and 'Recommencer depuis la 1re Heure' not in x['inc'],None)
   ck(lab,'complete_truth','24/24' in x['comp'] and 'LE CYCLE DES 24 HEURES EST ACCOMPLI' in x['comp'] and 'Recommencer depuis la 1re Heure' in x['comp'],None)
   ck(lab,'terminal_nav_no_next',not any('Suivante' in q for q in x['nav']) and len(x['nav'])==2,x['nav'])
   ck(lab,'no_local_home','Revenir à l’Accueil' not in x['inc'] and 'Revenir à l’Accueil' not in x['comp'],None)
   ck(lab,'no_horizontal_overflow',x['overflow'],None)
   y=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));state.currentHour=24;state.view='reader';renderReader(CORPUS.hours.find(h=>h.hour_number===24),false);markMeditee(24);const a=document.getElementById('hour24CyclePanelHost').innerText;markMeditee(24);const b=document.getElementById('hour24CyclePanelHost').innerText;return {a,b}}""")
   ck(lab,'live_transition','24/24' in y['a'] and '23/24' in y['b'] and 'Recommencer' not in y['b'],y)
   z=await p.evaluate("""() => {state.readHours=new Set(Array.from({length:23},(_,i)=>i+1));state.notes={n:{text:'x'}};const before=JSON.stringify(buildPersonalSnapshotFromState());window.confirm=()=>true;const r=restartTwentyFourHours({requireComplete:true,destination:'hour1'});const after=JSON.stringify(buildPersonalSnapshotFromState());return {r,same:before===after}}""")
   ck(lab,'incomplete_restart_rejected',z['r'] is False and z['same'],z)
   ck(lab,'no_page_errors',not errs,errs)
   await c.close()
  await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows),'profiles':len(profiles)}
 OUT.write_text(json.dumps({'schema':'L24H_V101125_INDEPENDENT_HOUR24_PROBE_V1','version':VER,'implementation':'separate browser probe; does not call primary Hour-24 matrix','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 else 2)
asyncio.run(main())
