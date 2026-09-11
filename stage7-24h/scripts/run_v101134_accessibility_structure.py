#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); LEDGER=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.parent.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader(LEDGER.open(encoding='utf-8-sig')))
want=['PASSION24.HOUR.08.P007','PASSION24.HOUR.05.REF.P005','PASSION24.SECTION.BENEFITS.P102','PASSION24.TEXT.PROMISES_BENEFITS.BODY.P097','PASSION24.TEXT.RELATED_HOUR_21.BODY.P073','PASSION24.TEXT.PART_III_MARY_SORROWS.BODY.P212']
sel=[]
for pid in want:
    r=next(x for x in rows if x.get('record_id')==pid)
    sel.append({'pid':pid,'off':int(r['source_offset']),'renderer_family':r['renderer_family']})
async def main():
    out=[]; errs=[]
    def add(name,ok,detail=None):out.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
    async with async_playwright() as pw:
        b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        p=await b.new_page(viewport={'width':1200,'height':900});p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded')
        for i,x in enumerate(sel):
            d=await p.evaluate('''({pid,off,fam})=>{const t=getFullParaText(pid)||'';const d=document.createElement('div');d.className='para-text';if(fam==='ldc_intra_break')d.innerHTML=renderLdcFlowFragmentText(t,pid,[off],{[String(off)]:'paragraph_break'});else d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);let target=null,acc=0;const w=document.createTreeWalker(d,NodeFilter.SHOW_TEXT);while(w.nextNode()){const n=w.currentNode,st=acc,en=acc+n.data.length;acc=en;if(st<=off&&off<en&&n.parentElement?.classList.contains('visual-boundary-separator-space')){target=n.parentElement;break}}const z={target:!!target,textExact:d.textContent===t,ariaHidden:target?.getAttribute('aria-hidden')??null,role:target?.getAttribute('role')??null,tabIndex:target?.getAttribute('tabindex')??null,contenteditable:target?.getAttribute('contenteditable')??null,wrapperText:target?.textContent??null,onclick:target?.getAttribute('onclick')??null,tag:target?.tagName??null};d.remove();return z}''',{'pid':x['pid'],'off':x['off'],'fam':x['renderer_family']})
            add(f'{i}_target_present',d.get('target') is True,{'pid':x['pid'],'off':x['off'],**d})
            add(f'{i}_source_text_exact',d.get('textExact') is True,{'pid':x['pid'],**d})
            add(f'{i}_space_preserved',d.get('wrapperText')==' ',{'pid':x['pid'],**d})
            add(f'{i}_not_aria_hidden',d.get('ariaHidden') is None,{'pid':x['pid'],**d})
            add(f'{i}_noninteractive',all(d.get(k) is None for k in ['role','tabIndex','contenteditable','onclick']),{'pid':x['pid'],**d})
        add('page_errors_zero',len(errs)==0,errs)
        await b.close()
    sm={'pass':sum(x['status']=='PASS' for x in out),'fail':sum(x['status']=='FAIL' for x in out),'total':len(out)}
    obj={'schema':'L24H_V101134_ACCESSIBILITY_STRUCTURE_RECONCILIATION_V1','provenance':'Direct browser structure check on the preserved v101.133 renderer logic; does not claim physical VoiceOver/TalkBack evidence.','summary':sm,'rows':out,'physical_screen_reader_gate':'OPEN'}
    OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] else 0)
asyncio.run(main())
