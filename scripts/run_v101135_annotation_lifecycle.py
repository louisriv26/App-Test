#!/usr/bin/env python3
import asyncio,csv,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(sys.argv[1]).read_text(encoding='utf-8');LED=Path(sys.argv[2]);OUT=Path(sys.argv[3]);rows=list(csv.DictReader(LED.open(encoding='utf-8-sig')));OUT.parent.mkdir(parents=True,exist_ok=True)
SURF=['Main Hour meditation text','Réflexions et pratiques','Promesses et bienfaits — main section','Promesses et bienfaits — Library mirror','Linked Livre du Ciel — Hours 1–24','Part III Livre du Ciel']
reps=[next(x for x in rows if x['surface']==s) for s in SURF]
async def fresh(b):
 p=await b.new_page();await p.set_content(HTML,wait_until='domcontentloaded');await p.evaluate("()=>{commitDurableChange=()=>({ok:true});saveState=()=>({ok:true,mirrorFailures:[]});showToast=()=>{};}");return p
async def main():
 tests=[];errs=[]
 def add(surface,name,ok,detail=None):tests.append({'surface':surface,'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for i,r in enumerate(reps):
   surf=r['surface'];pid=r['record_id'];off=int(r['source_offset'])
   # APPLE exact-selection highlight via actual applyHighlight path.
   p=await fresh(b);p.on('pageerror',lambda e:errs.append(str(e)))
   apple=await p.evaluate('''({pid,off})=>{const t=getFullParaText(pid),st=Math.max(0,off-2),en=Math.min(t.length,off+4);state._pending={paraId:pid,start:st,end:en,text:t.slice(st,en),whole_paragraph:false,android_paragraph_mode:false,visual_paragraph:false};document.getElementById('cpRemoveBtn').dataset.hlId='';applyHighlight('yellow');const h=state.textHighlights[pid]?.[0];const snap=buildPersonalSnapshotFromState();return{st,en,expected:t.slice(st,en),h,snap}}''',{'pid':pid,'off':off})
   h=apple.get('h');add(surf,'apple_created_exact',bool(h) and h['start_offset']==apple['st'] and h['end_offset']==apple['en'] and h['selected_text_snapshot']==apple['expected'],h)
   add(surf,'apple_snapshot_contains',bool(apple['snap'].get('textHighlights',{}).get(pid)),None)
   await p.close()
   p=await fresh(b);rest=await p.evaluate('''({pid,snap})=>{applyPersonalSnapshot(snap);const h=state.textHighlights[pid]?.[0];const t=getFullParaText(pid);const d=document.createElement('div');d.className='para-text';d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);const marks=d.querySelectorAll('mark.hl').length;d.remove();return{h,marks}}''',{'pid':pid,'snap':apple['snap']})
   add(surf,'apple_fresh_document_restore',bool(rest.get('h')) and rest['h']['start_offset']==apple['st'] and rest['h']['end_offset']==apple['en'],rest)
   add(surf,'apple_rendered_highlight_present',rest['marks']>=1,rest['marks'])
   rem=await p.evaluate('''pid=>{const h=state.textHighlights[pid]?.[0];if(h)removeStoredHighlightById(pid,h.id);const t=getFullParaText(pid),d=document.createElement('div');d.className='para-text';d.innerHTML=renderParaText(t,pid);document.body.appendChild(d);const m=d.querySelectorAll('mark.hl').length;d.remove();return{stored:(state.textHighlights[pid]||[]).length,marks:m}}''',pid)
   add(surf,'apple_remove_store_clean',rem['stored']==0,rem);add(surf,'apple_no_orphan_mark',rem['marks']==0,rem);await p.close()
   # SAMSUNG whole visual-paragraph highlight via actual applyHighlight path.
   p=await fresh(b);sam=await p.evaluate('''({pid,off})=>{const t=getFullParaText(pid),cuts=getPresentationLocalBreaks(pid),bounds=[0,...cuts,t.length];let a=0,b=t.length;for(let i=0;i<bounds.length-1;i++){if(off>=bounds[i]&&off<bounds[i+1]){a=bounds[i];b=bounds[i+1];break}};if(a===off&&a<t.length&&t[a]===' '){}state._pending={paraId:pid,start:a,end:b,text:t.slice(a,b),whole_paragraph:true,android_paragraph_mode:true,visual_paragraph:true};document.getElementById('cpRemoveBtn').dataset.hlId='';applyHighlight('blue');const h=state.textHighlights[pid]?.[0],snap=buildPersonalSnapshotFromState();return{a,b,h,snap}}''',{'pid':pid,'off':off})
   sh=sam.get('h');add(surf,'samsung_created_whole_visual_paragraph',bool(sh) and sh.get('whole_paragraph') and sh.get('android_paragraph_mode') and sh.get('visual_paragraph') and sh['start_offset']==sam['a'] and sh['end_offset']==sam['b'],sh);await p.close()
   p=await fresh(b);sr=await p.evaluate('''({pid,snap})=>{applyPersonalSnapshot(snap);const h=state.textHighlights[pid]?.[0];return h||null}''',{'pid':pid,'snap':sam['snap']});add(surf,'samsung_fresh_document_restore',bool(sr) and sr.get('whole_paragraph') and sr.get('android_paragraph_mode'),sr)
   srem=await p.evaluate('''pid=>{const h=state.textHighlights[pid]?.[0];if(h)removeStoredHighlightById(pid,h.id);return(state.textHighlights[pid]||[]).length}''',pid);add(surf,'samsung_remove_clean',srem==0,srem);await p.close()
   # Paragraph-note lifecycle via actual saveNoteFromModal/deleteNote. Range-note offsets are not a product feature.
   p=await fresh(b);note=await p.evaluate('''({pid,i})=>{_noteModalParaId=pid;document.getElementById('noteTextarea').value='qa-note-'+i;saveNoteFromModal();const n=state.notes[pid]?.[0];const snap=buildPersonalSnapshotFromState();return{n,snap}}''',{'pid':pid,'i':i});add(surf,'note_created_actual_api',bool(note.get('n')) and note['n']['text']==f'qa-note-{i}',note.get('n'));await p.close()
   p=await fresh(b);nr=await p.evaluate('''({pid,snap})=>{applyPersonalSnapshot(snap);return state.notes[pid]?.[0]||null}''',{'pid':pid,'snap':note['snap']});add(surf,'note_fresh_document_restore',bool(nr) and nr['text']==f'qa-note-{i}',nr)
   ndel=await p.evaluate('''({pid,id})=>{deleteNote(pid,id);return(state.notes[pid]||[]).length}''',{'pid':pid,'id':nr['id'] if nr else ''});add(surf,'note_remove_clean',ndel==0,ndel);add(surf,'range_note_contract_not_claimed',True,{'supported_model':'paragraph-level notes; no range-offset note schema'});await p.close()
  await b.close()
 sm={'pass':sum(x['status']=='PASS' for x in tests),'fail':sum(x['status']=='FAIL' for x in tests),'total':len(tests),'surfaces':len(reps),'page_errors':errs,'fresh_document_rehydration':'serialized personal snapshot applied to a new document; true installed-PWA storage reload remains external'}
 OUT.write_text(json.dumps({'schema':'L24H_V101135_ANNOTATION_LIFECYCLE_V1','summary':sm,'rows':tests},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(sm));raise SystemExit(2 if sm['fail'] or errs else 0)
asyncio.run(main())
