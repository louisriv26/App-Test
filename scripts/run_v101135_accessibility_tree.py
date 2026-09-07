#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');LED=Path(sys.argv[2]);OUT=Path(sys.argv[3]);rows=list(csv.DictReader(LED.open(encoding='utf-8-sig')));OUT.parent.mkdir(parents=True,exist_ok=True)
SURF=['Main Hour meditation text','Réflexions et pratiques','Promesses et bienfaits — main section','Promesses et bienfaits — Library mirror','Linked Livre du Ciel — Hours 1–24','Part III Livre du Ciel']
reps=[next(x for x in rows if x['surface']==s) for s in SURF]
JS=r'''r=>{document.body.innerHTML='<main id="axroot"></main>';const h=document.getElementById('axroot'),pid=r.record_id,off=Number(r.source_offset),t=getFullParaText(pid)||'',d=document.createElement('div');d.id='target';d.className='para-text';d.innerHTML=r.renderer_family==='ldc_intra_break'?renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'}):renderParaText(t,pid);h.appendChild(d);return{source:t,text:d.textContent,wrapperCount:d.querySelectorAll('.visual-boundary-separator-space').length}}'''
def ax_text(nodes):
 vals=[]
 for n in nodes:
  if n.get('role',{}).get('value') in ('StaticText','InlineTextBox'):
   v=n.get('name',{}).get('value','')
   if v: vals.append(v)
 return vals
async def main():
 res=[];errs=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page();p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded');cdp=await p.context.new_cdp_session(p);await cdp.send('Accessibility.enable')
  for r in reps:
   meta=await p.evaluate(JS,r);before=ax_text((await cdp.send('Accessibility.getFullAXTree'))['nodes'])
   await p.evaluate("()=>{const w=document.querySelector('#target .visual-boundary-separator-space');if(w)w.replaceWith(document.createTextNode(w.textContent));}")
   after=ax_text((await cdp.send('Accessibility.getFullAXTree'))['nodes'])
   # StaticText may segment differently; compare concatenated accessible text and token multiplicity.
   bt=''.join(before);at=''.join(after);ok=(meta['source']==meta['text'] and meta['wrapperCount']>=1 and bt==at and bt.count(meta['source'].strip()[:12])==at.count(meta['source'].strip()[:12]))
   res.append({'surface':r['surface'],'record_id':r['record_id'],'status':'PASS' if ok else 'FAIL','before_text':bt,'after_text':at,'source_text_exact':meta['source']==meta['text']})
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in res),'fail':sum(x['status']=='FAIL' for x in res),'total':len(res),'page_errors':errs}
 OUT.write_text(json.dumps({'schema':'L24H_V101135_ACCESSIBILITY_TREE_V1','summary':sm,'rows':res},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] or errs else 0)
asyncio.run(main())
