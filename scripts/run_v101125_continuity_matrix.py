#!/usr/bin/env python3
import asyncio,json,re,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); VERSION='v101.125'
EXPECTED=[
 ['PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013'],
 ['PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013'],
 ['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015'],
 ['PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184'],
 ['PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186'],
]
profiles=[('phone',390,844),('ipad_portrait',820,1180),('ipad_landscape',1180,820),('desktop',1200,900),('samsung',412,915)]
async def main():
 rows=[]
 def add(profile,pair,check,ok,detail=None): rows.append({'profile':profile,'pair':'→'.join(pair),'check':check,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h in profiles:
   page=await browser.new_page(viewport={'width':w,'height':h})
   errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded'); await page.wait_for_timeout(50)
   groups=await page.evaluate('CONTINUITY_GROUPS')
   add(label,['UNIVERSE','UNIVERSE'],'exact_five_pair_universe',groups==EXPECTED,groups)
   for aid,bid in EXPECTED:
    hour=int(re.search(r'HOUR\.(\d+)',aid).group(1)); await page.evaluate(f'openHour({hour},false)'); await page.wait_for_timeout(30)
    d=await page.evaluate('''([a,b])=>{
      const A=document.getElementById(a),B=document.getElementById(b); const S=A&&A.closest('.continuity-flow-surface');
      const TA=A&&A.querySelector('.para-text'),TB=B&&B.querySelector('.para-text'); const J=S&&S.querySelector('.continuity-flow-joiner');
      const ia=getTargetInfo(a),ib=getTargetInfo(b); const ar=TA?[...TA.getClientRects()]:[],br=TB?[...TB.getClientRects()]:[]; const al=ar[ar.length-1],bf=br[0]; const lh=TA?parseFloat(getComputedStyle(TA).lineHeight)||0:0;
      return {A:!!A,B:!!B,S:!!S,version:APP_VERSION,aDisplay:A&&getComputedStyle(A).display,bDisplay:B&&getComputedStyle(B).display,taDisplay:TA&&getComputedStyle(TA).display,tbDisplay:TB&&getComputedStyle(TB).display,join:J&&J.textContent,numberCount:S?S.querySelectorAll('.para-num').length:0,aText:TA&&TA.textContent,bText:TB&&TB.textContent,expectedA:ia&&ia.text,expectedB:ib&&ib.text,dy:(al&&bf)?bf.y-al.y:null,lineHeight:lh,dups:[...document.querySelectorAll('#'+CSS.escape(a))].length+[...document.querySelectorAll('#'+CSS.escape(b))].length,outerGap:S?parseFloat(getComputedStyle(S).marginBottom)||0:null};
    }''',[aid,bid])
    add(label,[aid,bid],'stable_ids_and_single_surface',d['A'] and d['B'] and d['S'] and d['dups']==2,d)
    add(label,[aid,bid],'true_inline_fragments',d['aDisplay']=='inline' and d['bDisplay']=='inline' and d['taDisplay']=='inline' and d['tbDisplay']=='inline',d)
    add(label,[aid,bid],'exact_single_space_joiner',d['join']==' ',d['join'])
    add(label,[aid,bid],'canonical_text_preserved',d['aText']==d['expectedA'] and d['bText']==d['expectedB'],{'a':d['aText'],'b':d['bText']})
    add(label,[aid,bid],'no_paragraph_gap_at_join',d['dy'] is not None and d['dy'] <= d['lineHeight']+1,{'dy':d['dy'],'lineHeight':d['lineHeight']})
    add(label,[aid,bid],'one_reperes_number_surface',d['numberCount']==1,d['numberCount'])
    # repères on: one number only, ids survive
    r=await page.evaluate('''([a,b])=>{setShowReperes(true); applyReperes(); const A=document.getElementById(a),S=A.closest('.continuity-flow-surface'); const n=S.querySelectorAll('.para-num');return{n:n.length,visible:[...n].filter(x=>getComputedStyle(x).display!=='none').length,a:!!A,b:!!document.getElementById(b)}}''',[aid,bid])
    add(label,[aid,bid],'reperes_keeps_one_visible_number',r['n']==1 and r['visible']==1 and r['a'] and r['b'],r)
    await page.evaluate('setShowReperes(false); applyReperes()')
    # deep link/source surface and highlight identity
    ident=await page.evaluate('''([a,b])=>{const A=document.getElementById(a),B=document.getElementById(b),ta=A.querySelector('[data-para-id]'),tb=B.querySelector('[data-para-id]');return{aBlock:ta.closest('.para-block').id,bBlock:tb.closest('.para-block').id,aData:ta.dataset.paraId,bData:tb.dataset.paraId,aFull:getFullParaText(a),bFull:getFullParaText(b)}}''',[aid,bid])
    add(label,[aid,bid],'annotation_identity_preserved',ident['aBlock']==aid and ident['bBlock']==bid and ident['aData']==aid and ident['bData']==bid and bool(ident['aFull']) and bool(ident['bFull']),ident)
   # notes test on H15 pair - visible dots must not become block split
   await page.evaluate('''()=>{state.notes['PASSION24.HOUR.15.P014']=[{id:'n1',text:'x'}];state.notes['PASSION24.HOUR.15.P015']=[{id:'n2',text:'y'}];openHour(15,false)}''')
   nd=await page.evaluate('''()=>{const a=document.getElementById('PASSION24.HOUR.15.P014'),b=document.getElementById('PASSION24.HOUR.15.P015'),s=a.closest('.continuity-flow-surface'),ta=a.querySelector('.para-text'),tb=b.querySelector('.para-text');const ar=[...ta.getClientRects()],br=[...tb.getClientRects()],al=ar[ar.length-1],bf=br[0];return{dots:[...s.querySelectorAll('.para-note-dot')].map(x=>({display:getComputedStyle(x).display,float:getComputedStyle(x).float})),dy:bf.y-al.y,line:parseFloat(getComputedStyle(ta).lineHeight)}}''')
   add(label,['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015'],'notes_do_not_restore_paragraph_gap',len(nd['dots'])==2 and all(x['display']!='none' and x['float']=='right' for x in nd['dots']) and nd['dy']<=nd['line']+1,nd)
   add(label,['PAGE','PAGE'],'no_page_errors',not errors,errors)
   await page.close()
  await browser.close()
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps({'version':VERSION,'rows':rows,'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}))
 raise SystemExit(0 if all(r['status']=='PASS' for r in rows) else 2)
asyncio.run(main())
