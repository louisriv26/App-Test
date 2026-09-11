#!/usr/bin/env python3
from pathlib import Path
import asyncio,json,sys
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8'); OUT=Path(sys.argv[2])
OPS=[
 ('PASSION24.HOUR.08.P009',37,48),('PASSION24.HOUR.08.P010',42,56),('PASSION24.HOUR.08.P015',43,57),
 ('PASSION24.HOUR.21.P020',62,76),('PASSION24.HOUR.21.P025',111,126),
 ('PASSION24.TEXT.RELATED_HOUR_06.BODY.P043',44,51),('PASSION24.TEXT.RELATED_HOUR_06.BODY.P058',44,51)]
HOUR={'PASSION24.HOUR.08.P009':8,'PASSION24.HOUR.08.P010':8,'PASSION24.HOUR.08.P015':8,'PASSION24.HOUR.21.P020':21,'PASSION24.HOUR.21.P025':21}
async def main():
 rows=[]
 def add(case,ok,detail=None):rows.append({'case':case,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  p=await b.new_page(viewport={'width':1200,'height':900});errs=[];p.on('pageerror',lambda e:errs.append(str(e)));await p.set_content(HTML,wait_until='domcontentloaded');await p.wait_for_timeout(80)
  # Stored highlight freshness and snapshot/note anchor roundtrip across every affected paragraph.
  for i,(pid,start,end) in enumerate(OPS,1):
   d=await p.evaluate('''({pid,start,end,i})=>{const t=getFullParaText(pid);const hl={id:'qa_h'+i,target_id:pid,target_type:getHighlightTargetType(pid),start_offset:start,end_offset:end,start,end,color:'yellow',text:t.slice(start,end),selected_text_snapshot:t.slice(start,end),text_hash:stableTextHash(t),paragraph_fingerprint:stableTextHash(t),para_hash:stableTextHash(t.slice(start,end)),schema_version:STORAGE_SCHEMA_VERSION,created_at:'2026-09-03T00:00:00Z',updated_at:'2026-09-03T00:00:00Z'};state.textHighlights={[pid]:[hl]};state.notes={[pid]:[{id:'qa_n'+i,text:'ancre',ts:1}]};const st=currentHighlightStatus(pid,hl);const snap=buildPersonalSnapshotFromState();const clean=sanitizePersonalSnapshot(snap);state.textHighlights={};state.notes={};applyPersonalSnapshot(clean);const rh=state.textHighlights[pid]&&state.textHighlights[pid][0],rn=state.notes[pid]&&state.notes[pid][0];return{fresh:st.fresh,start:rh&&rh.start_offset,end:rh&&rh.end_offset,text:rh&&rh.selected_text_snapshot,noteId:rn&&rn.id,noteText:rn&&rn.text,expected:t.slice(start,end),hash:rh&&rh.text_hash,currentHash:stableTextHash(t)}}''',{'pid':pid,'start':start,'end':end,'i':i})
   add(pid+'_highlight_fresh_after_topology_change',d['fresh'] and d['start']==start and d['end']==end and d['text']==d['expected'] and d['hash']==d['currentHash'],d)
   add(pid+'_note_anchor_snapshot_roundtrip',d['noteId']==f'qa_n{i}' and d['noteText']=='ancre',d)
  # Apple/WebKit exact selection semantics on real Hour DOM surfaces around former break positions.
  for pid,start,end in [x for x in OPS if x[0] in HOUR]:
   await p.evaluate('(n)=>openHour(n,false)',HOUR[pid]);await p.wait_for_timeout(25)
   d=await p.evaluate('''({pid,start,end})=>{const t=getFullParaText(pid),r=makeDomRangeForParaOffsets(pid,start,end);if(!r)return{ok:false,why:'no_range'};state._pending=null;const ok=setPendingSelectionFromRange(r,null,false);return{ok,start:state._pending&&state._pending.start,end:state._pending&&state._pending.end,text:state._pending&&state._pending.text,expected:t.slice(start,end),rangeText:r.toString()}}''',{'pid':pid,'start':start,'end':end})
   add(pid+'_apple_exact_selection_offsets',d.get('ok') and d.get('start')==start and d.get('end')==end and d.get('text')==d.get('expected').strip(),d)
  add('no_page_errors',not errs,errs);await b.close()
 summary={'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
 OUT.write_text(json.dumps({'schema':'L24H_V101129_USER_STATE_ANCHOR_APPLE_SELECTION_V1','version':'v101.129','scope':'Chromium semantic simulation of persisted anchors and WebKit-style exact selection offsets; physical Apple/Samsung remain external','summary':summary,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
 if summary['fail']:
  for r in rows:
   if r['status']=='FAIL':print('FAIL',r)
  raise SystemExit(2)
asyncio.run(main())
