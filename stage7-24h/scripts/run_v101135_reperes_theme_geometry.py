#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');LEDGER=Path(sys.argv[2]);OUT=Path(sys.argv[3]);rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')));OUT.parent.mkdir(parents=True,exist_ok=True)
STATES=[('light',False),('light',True),('dark',False),('dark',True)]
JS=r'''([rows,theme,rep])=>{document.documentElement.setAttribute('data-theme',theme);const app=document.getElementById('app');app.classList.toggle('reperes-on',rep);return rows.map(r=>{const pid=r.record_id,off=Number(r.source_offset),t=getFullParaText(pid)||'',d=document.createElement('div');d.className='para-text';d.style.cssText='position:absolute;left:40px;top:20px;width:700px;';if(r.renderer_family==='ldc_intra_break')d.innerHTML=renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'});else d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);let b=0,w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n,first=null;while(n=w.nextNode()){let e=b+n.data.length;if(off+1>=b&&off+1<e){let rg=document.createRange();rg.setStart(n,off+1-b);rg.setEnd(n,off+2-b);let q=rg.getBoundingClientRect();first={x:q.x,ch:n.data[off+1-b]};break}b=e}let dx=first?first.x-d.getBoundingClientRect().x:null;const exact=d.textContent===t;d.remove();return{pid,off,dx,textExact:exact,status:(dx!==null&&Math.abs(dx)<=1&&exact)?'PASS':'FAIL'}})}'''
async def main():
 res=[];errs=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=await b.new_page(viewport={'width':1200,'height':900});p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded')
  for theme,rep in STATES:
   rr=await p.evaluate(JS,[rows,theme,rep])
   for x in rr:x.update({'theme':theme,'reperes_on':rep})
   res+=rr
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in res),'fail':sum(x['status']=='FAIL' for x in res),'total':len(res),'states':len(STATES),'loci':len(rows),'page_errors':errs}
 OUT.write_text(json.dumps({'schema':'L24H_V101135_REPERES_THEME_GEOMETRY_V1','summary':sm,'rows':res},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] or errs or len(rows)!=82 else 0)
asyncio.run(main())
