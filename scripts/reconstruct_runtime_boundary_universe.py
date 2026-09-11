#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2]); OUT.parent.mkdir(parents=True,exist_ok=True)
RAWOUT=OUT.with_name(OUT.stem+'_RAW_MARKERS.csv'); EXCOUT=OUT.with_name(OUT.stem+'_EXCLUSIONS.csv'); SUMOUT=OUT.with_name(OUT.stem+'_SUMMARY.json')
JS=r'''([routeType,routeId])=>{
 const root=document.getElementById('content'); if(!root)return [];
 function pidFor(e){const x=e.closest('.para-block[id],[id^="PASSION24."]');return x?x.id:''}
 function textRoot(e){return e.closest('.para-text')}
 function offsetBefore(tr,e){if(!tr)return null;try{const rg=document.createRange();rg.setStart(tr,0);rg.setEndBefore(e);return rg.toString().length}catch(_){return null}}
 function surface(e){for(const id of ['meditationContent','reflectionsContent','linkedTextsContent'])if(e.closest('#'+id))return id;return routeType}
 function firstVisibleAfter(tr,e){if(!tr)return null;const walker=document.createTreeWalker(tr,NodeFilter.SHOW_TEXT);let seen=false,n,acc=0;function locallySuppressed(node){let x=node.parentElement;while(x&&x!==tr){if(x.getAttribute&&x.getAttribute('aria-hidden')==='true')return true;if(x.classList&&x.classList.contains('speech-quote-hidden'))return true;x=x.parentElement}return false}while(n=walker.nextNode()){const start=acc,end=acc+n.data.length;acc=end;if(!seen){try{const rel=e.compareDocumentPosition(n);if(rel & Node.DOCUMENT_POSITION_FOLLOWING)seen=true;else continue}catch(_){continue}}if(locallySuppressed(n))continue;for(let i=0;i<n.data.length;i++){const ch=n.data[i];if(/\s/u.test(ch))continue;return{offset:start+i,ch,width:null,x:null,y:null}}}return null}
 const nodes=[...root.querySelectorAll('.speech-presentation-visual-break,.ldc-visual-paragraph-break,.para-seg')];const out=[];
 for(const e of nodes){let fam='',tr=textRoot(e),pid=pidFor(e),off=null;
  if(e.classList.contains('para-seg')){const segs=[...e.parentElement.children].filter(x=>x.classList&&x.classList.contains('para-seg'));if(segs[0]===e)continue;fam='display_segment';off=offsetBefore(tr,e)}
  else if(e.classList.contains('speech-cross-record-visual-break'))fam='speech_cross_record';
  else if(e.classList.contains('speech-presentation-visual-break')){fam='speech_presentation_break';off=offsetBefore(tr,e)}
  else if(e.classList.contains('ldc-visual-paragraph-break')){fam=tr?'ldc_intra_break':'ldc_cross_record';off=tr?offsetBefore(tr,e):null}
  if(!fam)continue;const cs=getComputedStyle(e),text=pid?(getFullParaText(pid)||''):'',ch=off!=null&&off>=0&&off<text.length?text[off]:'',fv=(fam==='speech_presentation_break'||fam==='ldc_intra_break')?firstVisibleAfter(tr,e):null;
  out.push({route_type:routeType,route_id:routeId,surface:surface(e),renderer_family:fam,record_id:pid,source_offset:off,source_char:ch,source_codepoint:ch?('U+'+ch.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')):'',display:cs.display,action:e.dataset.ldcBoundaryAction||'',dom_class:e.className,first_visible_exists:!!fv,first_visible_offset:fv?fv.offset:null,first_visible_char:fv?fv.ch:'',first_visible_width:fv?fv.width:null});
 }return out;
}'''
async def main():
 rows=[];errors=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);p=await b.new_page(viewport={'width':1200,'height':900});p.on('pageerror',lambda e:errors.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded')
  for n in range(1,25):await p.evaluate('(n)=>openHour(n,false)',n);rows+=await p.evaluate(JS,['hour',str(n)])
  for sid in await p.evaluate('()=>CORPUS.sections.map(x=>x.section_id)'):await p.evaluate('(x)=>openSection(x,false)',sid);rows+=await p.evaluate(JS,['section',sid])
  for pid in await p.evaluate('()=>CORPUS.prayers.map(x=>x.prayer_id)'):await p.evaluate('(x)=>openPrayer(x,false)',pid);rows+=await p.evaluate(JS,['prayer',pid])
  for lid in await p.evaluate('()=>TEXT_LIBRARY.filter(x=>Array.isArray(x.body)).map(x=>x.id)'):await p.evaluate('(x)=>openLibraryText(x,false)',lid);rows+=await p.evaluate(JS,['library',lid])
  await b.close()
 # Effective visual boundary = block-level marker, except a local speech/LDC boundary with no visible content glyph after it in the same source record.
 effective=[];excluded=[]
 for r in rows:
  reason=None
  if r['display']!='block': reason='NON_BLOCK_MARKER'
  elif r['renderer_family'] in ('speech_presentation_break','ldc_intra_break') and not r['first_visible_exists']: reason='NO_VISIBLE_CONTENT_AFTER_LOCAL_BOUNDARY'
  if reason:
   q=dict(r);q['exclusion_reason']=reason;excluded.append(q)
  else:effective.append(r)
 effective.sort(key=lambda r:(r['route_type'],r['route_id'],r['surface'],r['record_id'], -1 if r['source_offset'] is None else int(r['source_offset']),r['renderer_family']))
 excluded.sort(key=lambda r:(r['exclusion_reason'],r['route_type'],r['route_id'],r['record_id'], -1 if r['source_offset'] is None else int(r['source_offset'])))
 raw_fields=['route_type','route_id','surface','renderer_family','record_id','source_offset','source_char','source_codepoint','display','action','dom_class','first_visible_exists','first_visible_offset','first_visible_char','first_visible_width']
 with RAWOUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=raw_fields);w.writeheader();w.writerows({k:r.get(k,'') for k in raw_fields} for r in rows)
 with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=raw_fields);w.writeheader();w.writerows({k:r.get(k,'') for k in raw_fields} for r in effective)
 exc_fields=raw_fields+['exclusion_reason']
 with EXCOUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=exc_fields);w.writeheader();w.writerows({k:r.get(k,'') for k in exc_fields} for r in excluded)
 from collections import Counter
 sm={'schema':'L24H_RUNTIME_BOUNDARY_UNIVERSE_RECONCILIATION_R2','raw_dom_markers':len(rows),'effective_runtime_boundaries':len(effective),'excluded_markers':len(excluded),'effective_families':dict(Counter(r['renderer_family'] for r in effective)),'excluded_reasons':dict(Counter(r['exclusion_reason'] for r in excluded)),'excluded_families':dict(Counter(r['renderer_family'] for r in excluded)),'page_errors':errors}
 SUMOUT.write_text(json.dumps(sm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm,ensure_ascii=False,indent=2))
 if len(rows)!=1858 or len(effective)!=1748 or len(excluded)!=110 or errors:raise SystemExit(2)
asyncio.run(main())
