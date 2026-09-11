#!/usr/bin/env python3
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); OUT.parent.mkdir(parents=True,exist_ok=True)
FONTS=[16,19,30]
JS=r'''([routeType,routeId])=>{
 const root=document.getElementById('content'); if(!root)return [];
 function pidFor(e){const x=e.closest('.para-block[id],[id^="PASSION24."]');return x?x.id:''}
 function textRoot(e){return e.closest('.para-text')}
 function offsetBefore(tr,e){if(!tr)return null;try{const rg=document.createRange();rg.setStart(tr,0);rg.setEndBefore(e);return rg.toString().length}catch(_){return null}}
 function hidden(node,stop){let x=node.parentElement;while(x&&x!==stop){if(x.getAttribute&&x.getAttribute('aria-hidden')==='true')return true;if(x.classList&&x.classList.contains('speech-quote-hidden'))return true;x=x.parentElement}return false}
 function firstGlyphAfter(e,scope){const w=document.createTreeWalker(scope,NodeFilter.SHOW_TEXT);let n,seen=false;while(n=w.nextNode()){if(!seen){try{const rel=e.compareDocumentPosition(n);if(rel & Node.DOCUMENT_POSITION_FOLLOWING)seen=true;else continue}catch(_){continue}}if(hidden(n,scope))continue;for(let i=0;i<n.data.length;i++){if(/\s/u.test(n.data[i]))continue;const rg=document.createRange();rg.setStart(n,i);rg.setEnd(n,i+1);const q=rg.getBoundingClientRect();return{node:n,off:i,ch:n.data[i],x:q.x,y:q.y,width:q.width}}}return null}
 function localFirstAfter(tr,e){if(!tr)return null;const w=document.createTreeWalker(tr,NodeFilter.SHOW_TEXT);let n,seen=false;while(n=w.nextNode()){if(!seen){try{const rel=e.compareDocumentPosition(n);if(rel & Node.DOCUMENT_POSITION_FOLLOWING)seen=true;else continue}catch(_){continue}}if(hidden(n,tr))continue;for(let i=0;i<n.data.length;i++){if(/\s/u.test(n.data[i]))continue;const rg=document.createRange();rg.setStart(n,i);rg.setEnd(n,i+1);const q=rg.getBoundingClientRect();return{node:n,off:i,ch:n.data[i],x:q.x,y:q.y,width:q.width}}}return null}
 const nodes=[...root.querySelectorAll('.speech-presentation-visual-break,.ldc-visual-paragraph-break,.para-seg')];const out=[];
 for(const e of nodes){let fam='',tr=textRoot(e),pid=pidFor(e),off=null;
  if(e.classList.contains('para-seg')){const segs=[...e.parentElement.children].filter(x=>x.classList&&x.classList.contains('para-seg'));if(segs[0]===e)continue;fam='display_segment';off=offsetBefore(tr,e)}
  else if(e.classList.contains('speech-cross-record-visual-break'))fam='speech_cross_record';
  else if(e.classList.contains('speech-presentation-visual-break')){fam='speech_presentation_break';off=offsetBefore(tr,e)}
  else if(e.classList.contains('ldc-visual-paragraph-break')){fam=tr?'ldc_intra_break':'ldc_cross_record';off=tr?offsetBefore(tr,e):null}
  if(!fam)continue; const cs=getComputedStyle(e); if(cs.display!=='block')continue;
  let fg=null,targetX=null;
  if(fam==='speech_presentation_break'||fam==='ldc_intra_break'){
    fg=localFirstAfter(tr,e); if(!fg)continue; targetX=tr.getBoundingClientRect().x;
  } else if(fam==='display_segment'){
    fg=firstGlyphAfter(e,e); if(!fg)continue; targetX=e.getBoundingClientRect().x;
  } else {
    fg=firstGlyphAfter(e,root); if(!fg)continue; let p=fg.node.parentElement; let tx=p&&p.closest?p.closest('.para-text'):null; targetX=tx?tx.getBoundingClientRect().x:fg.x;
  }
  const dx=fg.x-targetX;out.push({route_type:routeType,route_id:routeId,renderer_family:fam,record_id:pid,source_offset:off,first_char:fg.ch,dx_px:dx,status:Math.abs(dx)<=1?'PASS':'FAIL'});
 }return out;
}'''
async def main():
 rows=[]; errors=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  p=await b.new_page(viewport={'width':1200,'height':900});p.on('pageerror',lambda e:errors.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded')
  routes=[]
  for n in range(1,25):routes.append(('hour',str(n),f'(n)=>openHour(Number(n),false)'))
  sections=await p.evaluate('()=>CORPUS.sections.map(x=>x.section_id)')
  for x in sections:routes.append(('section',x,'x=>openSection(x,false)'))
  prayers=await p.evaluate('()=>CORPUS.prayers.map(x=>x.prayer_id)')
  for x in prayers:routes.append(('prayer',x,'x=>openPrayer(x,false)'))
  libs=await p.evaluate('()=>TEXT_LIBRARY.filter(x=>Array.isArray(x.body)).map(x=>x.id)')
  for x in libs:routes.append(('library',x,'x=>openLibraryText(x,false)'))
  for fs in FONTS:
   await p.evaluate("fs=>document.documentElement.style.setProperty('--reading-size',fs+'px')",fs)
   cycle=[]
   for rt,rid,op in routes:
    await p.evaluate(op,rid); rr=await p.evaluate(JS,[rt,rid]);
    for x in rr:x['font_px']=fs
    cycle+=rr
   if len(cycle)!=1748:
    errors.append(f'font {fs}: effective geometry count {len(cycle)} != 1748')
   rows+=cycle
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'total':len(rows),'expected_total':1748*len(FONTS),'fonts':FONTS,'per_font_counts':{str(f):sum(x['font_px']==f for x in rows) for f in FONTS},'page_errors':errors}
 OUT.write_text(json.dumps({'schema':'L24H_V101135_FULL_1748_BOUNDARY_GEOMETRY_V1','summary':sm,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm,ensure_ascii=False));raise SystemExit(2 if sm['fail'] or errors or sm['total']!=sm['expected_total'] else 0)
asyncio.run(main())
