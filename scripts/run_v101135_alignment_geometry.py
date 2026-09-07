#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); LEDGER=Path(sys.argv[2]); OUT=Path(sys.argv[3]); MODE=sys.argv[4] if len(sys.argv)>4 else 'candidate'
rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
profiles=[('desktop',1200,900),('ipad_portrait',820,1180),('ipad_landscape',1180,820),('iphone',390,844),('samsung',412,915)]
fonts=[16,19,22,26,30]
async def main():
 res=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for lab,w,h in profiles:
   p=await b.new_page(viewport={'width':w,'height':h});errs=[];p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded');
   for fs in fonts:
    await p.evaluate("fs=>document.documentElement.style.setProperty('--reading-size',fs+'px')",fs)
    batch=await p.evaluate('''rows=>rows.map(r=>{const pid=r.record_id,off=Number(r.source_offset),t=getFullParaText(pid)||'';const d=document.createElement('div');d.className='para-text';d.style.cssText='position:absolute;left:40px;top:20px;width:700px;';if(r.renderer_family==='ldc_intra_break')d.innerHTML=renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'});else d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);function rectAt(o){let b=0,w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT),n;while(n=w.nextNode()){let e=b+n.data.length;if(o>=b&&o<e){let rr=document.createRange();rr.setStart(n,o-b);rr.setEnd(n,o-b+1);let q=rr.getBoundingClientRect();return{x:q.x,y:q.y,width:q.width,ch:n.data[o-b],cls:n.parentElement.className,aria:n.parentElement.getAttribute('aria-hidden')}}b=e}return null}const first=rectAt(off+1),sp=rectAt(off),dx=first?first.x-d.getBoundingClientRect().x:null,wrap=d.querySelector('.visual-boundary-separator-space'),out={pid,off,sourceChar:t[off],firstChar:t[off+1],dx,spaceWidth:sp&&sp.width,wrapperWidth:wrap&&wrap.getBoundingClientRect().width,textExact:d.textContent===t,wrapperAria:wrap&&wrap.getAttribute('aria-hidden'),wrapperCount:d.querySelectorAll('.visual-boundary-separator-space').length,breakCount:d.querySelectorAll('.speech-presentation-visual-break,.ldc-visual-paragraph-break').length};d.remove();return out})''',rows)
    for x in batch:
     ok=(x['dx'] is not None and abs(x['dx'])<=1 and x['textExact'] and x['sourceChar']==' ')
     if MODE=='baseline': ok=(x['dx'] is not None and x['dx']>1 and x['textExact'] and x['sourceChar']==' ')
     res.append({'profile':lab,'font_px':fs,'record_id':x['pid'],'source_offset':x['off'],'status':'PASS' if ok else 'FAIL','detail':x})
   await p.close()
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in res),'fail':sum(x['status']=='FAIL' for x in res),'total':len(res),'loci':len(rows),'profiles':len(profiles),'font_sizes':len(fonts)}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'schema':'L24H_V101135_ALIGNMENT_GEOMETRY_V1','mode':MODE,'summary':sm,'rows':res},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
