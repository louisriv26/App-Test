#!/usr/bin/env python3
import asyncio,json,re,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); VERSION=sys.argv[2]; OUT=Path(sys.argv[3])
PAIRS=[
 ['PASSION24.HOUR.03.P012','PASSION24.HOUR.03.P013'],
 ['PASSION24.HOUR.13.P011','PASSION24.HOUR.13.P013'],
 ['PASSION24.HOUR.15.P014','PASSION24.HOUR.15.P015'],
 ['PASSION24.HOUR.19.P183','PASSION24.HOUR.19.P184'],
 ['PASSION24.HOUR.19.P185','PASSION24.HOUR.19.P186'],
]
PROFILES=[('phone',390,844),('ipad_portrait',820,1180),('ipad_landscape',1180,820),('desktop',1600,1000),('samsung',412,915)]
CHAR_RECT=r'''(root,first)=>{const ns=[];const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())if(n.data.length)ns.push(n);n=first?ns.find(n=>n.data.trim().length):[...ns].reverse().find(n=>n.data.trim().length);if(!n)return null;let i=first?0:n.data.length-1;if(first){while(i<n.data.length&&/\s/.test(n.data[i]))i++}else{while(i>=0&&/\s/.test(n.data[i]))i--}const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);const x=r.getBoundingClientRect();return{x:x.x,y:x.y,right:x.right,bottom:x.bottom,width:x.width,height:x.height,ch:n.data[i]}}'''
async def main():
 rows=[]
 def add(profile,pair,check,ok,detail=None):rows.append({'profile':profile,'pair':'→'.join(pair),'check':check,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,w,h in PROFILES:
   page=await browser.new_page(viewport={'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(30)
   groups=await page.evaluate('CONTINUITY_GROUPS');add(label,['UNIVERSE','UNIVERSE'],'exact_five_pair_universe',groups==PAIRS,groups)
   for a,b in PAIRS:
    hr=int(re.search(r'HOUR\.(\d+)',a).group(1));await page.evaluate(f'openHour({hr},false)');await page.wait_for_timeout(15)
    d=await page.evaluate(f'''([a,b])=>{{const A=document.getElementById(a),B=document.getElementById(b),S=A&&A.closest('.continuity-flow-surface'),TA=A&&A.querySelector('.para-text'),TB=B&&B.querySelector('.para-text');const cr={CHAR_RECT};const ar=TA&&cr(TA,false),br=TB&&cr(TB,true);const aSegs=TA?[...TA.querySelectorAll(':scope > .para-seg')]:[];const bSegs=TB?[...TB.querySelectorAll(':scope > .para-seg')]:[];return{{version:APP_VERSION,A:!!A,B:!!B,S:!!S,ar,br,dy:ar&&br?br.y-ar.y:null,dx:ar&&br?br.x-ar.right:null,aDisplay:A&&getComputedStyle(A).display,bDisplay:B&&getComputedStyle(B).display,taDisplay:TA&&getComputedStyle(TA).display,tbDisplay:TB&&getComputedStyle(TB).display,aSegs:aSegs.map(x=>({{display:getComputedStyle(x).display,mt:getComputedStyle(x).marginTop,mb:getComputedStyle(x).marginBottom}})),bSegs:bSegs.map(x=>({{display:getComputedStyle(x).display,mt:getComputedStyle(x).marginTop,mb:getComputedStyle(x).marginBottom}})),join:S&&S.querySelector('.continuity-flow-joiner')&&S.querySelector('.continuity-flow-joiner').textContent,aText:TA&&TA.textContent,bText:TB&&TB.textContent,ea:getTargetInfo(a).text,eb:getTargetInfo(b).text}}}}''',[a,b])
    add(label,[a,b],'stable_ids_surface',d['A'] and d['B'] and d['S'],d)
    add(label,[a,b],'fragment_and_text_wrappers_inline',d['aDisplay']=='inline' and d['bDisplay']=='inline' and d['taDisplay']=='inline' and d['tbDisplay']=='inline',d)
    add(label,[a,b],'canonical_text_exact',d['aText']==d['ea'] and d['bText']==d['eb'])
    add(label,[a,b],'single_space_joiner',d['join']==' ',d['join'])
    if d['aSegs']:
      add(label,[a,b],'leader_final_display_segment_inline',d['aSegs'][-1]['display']=='inline',d['aSegs'])
      # Earlier segments remain block and internal rhythm remains present.
      add(label,[a,b],'leader_prior_segments_remain_block',all(x['display']=='block' for x in d['aSegs'][:-1]),d['aSegs'])
      if len(d['aSegs'])>=2:
       add(label,[a,b],'leader_internal_rhythm_preserved',float(d['aSegs'][-2]['mb'].replace('px',''))>0,d['aSegs'])
    else:
      add(label,[a,b],'leader_no_segment_override_needed',True)
    if d['bSegs']:
      add(label,[a,b],'follower_first_display_segment_inline',d['bSegs'][0]['display']=='inline',d['bSegs'])
    else:
      add(label,[a,b],'follower_no_segment_override_needed',True)
    # Exact glyph baseline is required on desktop, where the 880px reader width leaves ample room.
    if label=='desktop':
      add(label,[a,b],'true_same_line_boundary_when_space_available',d['dy'] is not None and abs(d['dy'])<=1.0,{'dy':d['dy'],'dx':d['dx'],'ar':d['ar'],'br':d['br']})
   add(label,['PAGE','PAGE'],'no_page_errors',not errors,errors)
   await page.close()
  await browser.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.write_text(json.dumps({'schema':'L24H_STRICT_CONTINUITY_GLYPH_FLOW_MATRIX_V1','version':VERSION,'profiles':[x[0] for x in PROFILES],'strict_invariant':'approved continuity boundaries must share a true inline glyph-flow; desktop wide profile requires same baseline when space is available','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
 if summary['fail']: raise SystemExit(2)
asyncio.run(main())
