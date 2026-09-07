#!/usr/bin/env python3
import asyncio,csv,json,sys,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
CAND=Path(sys.argv[1]).read_text(encoding='utf-8');BASE=Path(sys.argv[2]).read_text(encoding='utf-8');LED=Path(sys.argv[3]);OUT=Path(sys.argv[4]);rows=list(csv.DictReader(LED.open(encoding='utf-8-sig')));OUT.parent.mkdir(parents=True,exist_ok=True)
JS=r'''rows=>rows.map(r=>{const pid=r.record_id,off=Number(r.source_offset),t=getFullParaText(pid)||'',d=document.createElement('div');d.className='para-text';if(r.renderer_family==='ldc_intra_break')d.innerHTML=renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'});else d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);function point(abs){let b=0,w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n;while(n=w.nextNode()){let e=b+n.data.length;if(abs>=b&&abs<=e)return[n,Math.max(0,Math.min(n.data.length,abs-b))];b=e}return null}const st=Math.max(0,off-2),en=Math.min(t.length,off+4),a=point(st),z=point(en);let sel='';if(a&&z){const rg=document.createRange();rg.setStart(a[0],a[1]);rg.setEnd(z[0],z[1]);const s=getSelection();s.removeAllRanges();s.addRange(rg);sel=s.toString();s.removeAllRanges()}const tc=d.textContent,wrap=d.querySelector('.visual-boundary-separator-space');d.remove();return{pid,off,source:t,textExact:tc===t,selection:sel,expectedSelection:t.slice(st,en),st,en,wrapperText:wrap?wrap.textContent:null}})'''
async def main():
 out=[];errs=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);pc=await b.new_page();pb=await b.new_page();pc.on('pageerror',lambda e:errs.append('cand:'+str(e)));pb.on('pageerror',lambda e:errs.append('base:'+str(e)));await pc.set_content(CAND,wait_until='domcontentloaded');await pb.set_content(BASE,wait_until='domcontentloaded')
  cc=await pc.evaluate(JS,rows);bb=await pb.evaluate(JS,rows);await b.close()
 uniq=set()
 for r,c,q in zip(rows,cc,bb):
  key=(hashlib.sha256(c['source'].encode()).hexdigest(),c['off']);uniq.add(key)
  ok=c['textExact'] and c['selection']==q['selection'] and c['source'][c['off']:c['off']+2] in c['selection'] and c['st']==q['st'] and c['en']==q['en'] and c['source']==q['source'] and c['wrapperText']==' '
  out.append({'record_id':c['pid'],'source_offset':c['off'],'surface':r['surface'],'status':'PASS' if ok else 'FAIL','candidate_selection':c['selection'],'baseline_selection':q['selection'],'expected_selection':c['expectedSelection'],'source_length':len(c['source'])})
 sm={'pass':sum(x['status']=='PASS' for x in out),'fail':sum(x['status']=='FAIL' for x in out),'total':len(out),'rendered_occurrences':len(rows),'unique_exact_text_offset_loci':len(uniq),'page_errors':errs}
 OUT.write_text(json.dumps({'schema':'L24H_V101135_EXHAUSTIVE_SELECTION_OFFSETS_V1','summary':sm,'rows':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] or errs or len(rows)!=82 or len(uniq)!=76 else 0)
asyncio.run(main())
