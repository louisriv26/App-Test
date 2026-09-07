#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');OUT=Path(sys.argv[2]);OUT.parent.mkdir(parents=True,exist_ok=True)
async def main():
 rs=[]
 def add(n,o,d=None):rs.append({'check':n,'status':'PASS' if o else 'FAIL','detail':d})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page();await p.set_content(HTML,wait_until='domcontentloaded')
  x=await p.evaluate('''()=>{let speechMeta=Object.values(SPEECH_PRESENTATION_PROJECTION||{}).reduce((a,x)=>a+(x.breaks||[]).length,0),disp=Object.values(DISPLAY_SEGMENTS||{}).reduce((a,x)=>a+Math.max(0,x.length-1),0),ldcBefore=0,ldcBlock=0,ldcInline=0;for(const blks of Object.values(LDC_LIBRARY_FLOW_LAYOUT||{}))for(const bl of blks){ldcBefore+=(bl.break_before||[]).length;for(const [i,cuts] of Object.entries(bl.intra||{})){const acts=(bl.intra_actions||{})[i]||{};for(const cut of cuts){const a=String(acts[String(cut)]||'paragraph_break');if(a==='preserve_break')ldcInline++;else ldcBlock++;}}}return{speechMeta,displayDeclared:disp,ldcBefore,ldcBlock,ldcInline,crossSpeech:(VISIBLE_PARAGRAPH_TOPOLOGY.cross_record_breaks||[]).length,localTopo:Object.values(VISIBLE_PARAGRAPH_TOPOLOGY.local_breaks||{}).reduce((a,x)=>a+x.length,0),wrapperWidth:(()=>{const z=Object.assign(document.body.appendChild(document.createElement('span')),{className:'visual-boundary-separator-space',textContent:' '});const w=z.getBoundingClientRect().width;z.remove();return w})()}}''')
  add('display_segments_declared_124',x['displayDeclared']==124,x);add('cross_speech_exact_1',x['crossSpeech']==1,x);add('ldc_intra_block_48',x['ldcBlock']==48,x);add('ldc_intra_preserve_inline_97',x['ldcInline']==97,x);add('separator_css_zero_width',abs(x['wrapperWidth'])<=0.01,x['wrapperWidth'])
  # known static-only false positives must render without a synthetic break immediately before their governed U+0020 due display segmentation
  controls=[['PASSION24.HOUR.05.P028',483],['PASSION24.HOUR.07.P117',228],['PASSION24.HOUR.08.P015',None],['PASSION24.HOUR.13.P005',147],['PASSION24.HOUR.22.REF.P001',237]]
  q=await p.evaluate('''cs=>cs.map(([pid,off])=>{const t=getFullParaText(pid)||'',d=document.createElement('div');d.className='para-text';d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);const n=d.querySelectorAll('.speech-presentation-visual-break').length;const seg=d.querySelectorAll('.para-seg').length;d.remove();return{pid,off,n,seg}})''',controls)
  # H08 P015 offset is not hard-required; all five must retain display segments and no new separator wrapper
  for z in q:add('static_false_positive_'+z['pid'],z['seg']>=2 and z['n']==0,z)
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in rs),'fail':sum(x['status']=='FAIL' for x in rs),'total':len(rs)};OUT.write_text(json.dumps({'schema':'L24H_V101133_NEGATIVE_CONTROLS_V1','summary':sm,'rows':rs},indent=2)+'\n');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
