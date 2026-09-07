#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VER='v101.125'
PAIRS=[('PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013',3),('PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013',13),('PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015',15),('PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184',19),('PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186',19)]
def divine(sp): return sorted({x.get('speaker') for x in sp if x.get('speaker') in {'JESUS','FATHER','MARY'}})
async def main():
 rows=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  p=await b.new_page(viewport={'width':1200,'height':900}); await p.set_content(HTML,wait_until='domcontentloaded')
  for a,c,h in PAIRS:
   await p.evaluate('(h)=>openHour(h,false)',h); await p.evaluate('setShowReperes(true); applyReperes()')
   d=await p.evaluate('''([a,c])=>{const A=document.getElementById(a),S=A&&A.closest('.continuity-flow-surface');return{aSpeech:SPEECH_DATA[a]||[],cSpeech:SPEECH_DATA[c]||[],badges:S?[...S.querySelectorAll('.speaker-badge')].map(x=>x.textContent.trim()):[],numbers:S?S.querySelectorAll('.para-num').length:0};}''',[a,c])
   da=divine(d['aSpeech']); dc=divine(d['cSpeech']); distinct=sorted(set(dc)-set(da)); ok=(not distinct) and d['numbers']==1
   rows.append({'pair':a+'→'+c,'status':'PASS' if ok else 'FAIL','leader_divine_speakers':da,'follower_divine_speakers':dc,'follower_distinct_divine_speakers':distinct,'visible_badges':d['badges'],'number_surfaces':d['numbers']})
  await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 obj={'schema':'L24H_V101125_CONTINUITY_SPEAKER_HEADER_AUDIT_V1','version':VER,'summary':summary,'rows':rows};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary));raise SystemExit(0 if summary['fail']==0 else 2)
asyncio.run(main())
